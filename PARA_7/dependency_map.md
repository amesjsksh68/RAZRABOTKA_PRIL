# Карта зависимостей: StPlatform и PetClinic


## Часть 1. StPlatform: 

### Слои

| Слой | Классы (примеры) | Роль |
|---|---|---|
| Контроллеры | `web/AssignmentPageController`, `api/ApiSubmissionController` | Принимают HTTP-запрос, разбирают форму или JSON, выбирают ответ |
| Сервисы | `submission/SubmissionService`, `user/UserService`, `assignment/AssignmentService`, `aicheck/AiCheckService` | Бизнес-правила и транзакции |
| Вспомогательные компоненты | `submission/LinkValidator`, `submission/AttachmentStorage` | Проверка ссылок, файлы на диске |
| Репозитории | `submission/SubmissionRepository`, `submission/SubmissionAttachmentRepository`, `assignment/AssignmentRepository`, `user/UserRepository` | Доступ к БД через Spring Data JPA |
| Сущности | `submission/Submission`, `submission/SubmissionAttachment`, `assignment/Assignment`, `user/User` | Данные и небольшие правила (`Assignment.deadlinePassed`) |

"Сбоку" от слоёв: `config`, `security` (сквозная настройка) и `common` (исключения и токены).

### Цепочка вызовов

`POST /assignments/{id}/submit`:

```
AssignmentPageController.submitWork
  → UserService.byId → UserService.findById → UserRepository.findById
  → AssignmentPageController.splitLinks
  → SubmissionService.submit (@Transactional)
      → AssignmentRepository.findById
      → Assignment.isPublished
      → SubmissionService.ensureNotAlreadySent
          → SubmissionRepository.findFirstByStudentIdAndAssignmentIdOrderByCreatedAtDesc
      → Assignment.deadlinePassed
      → SubmissionService.normalizedLinks, SubmissionService.normalizedComment
      → LinkValidator.isValid
      → SubmissionRepository.save(new Submission(...))
      → AttachmentStorage.store (только если приложен файл)
      → SubmissionAttachmentRepository.save (только если приложен файл)
      → ApplicationEventPublisher.publishEvent(SubmissionCreatedEvent)
```

Продолжение после коммита транзакции, через событие:

```
AiCheckListener.onSubmissionCreated
  → AiCheckService.enqueueIfAbsent → AiCheckService.enqueue
      → SubmissionRepository.getReferenceById
      → AiCheckRepository.save
```

Второй вход, `POST /api/submissions`: `ApiSubmissionController.submit → UserService.byId` и `SubmissionService.submit`, дальше та же цепочка, но без файла. Оба контроллера используют один сервис, поэтому правила сдачи не дублируются.

### Все ли стрелки идут «вниз»?

**В основной цепочке — да:** контроллер → сервис → репозиторий. Контроллеры `web` и `api` не обращаются к репозиториям сущностей напрямую, а классы из `web` и `api` никто ниже не импортирует.

Однако, есть отклонения:

1. **Веб-тип в сервисе.** `SubmissionService.submit` и `AttachmentStorage.store` принимают `MultipartFile` из `org.springframework.web`. Вызов идёт вниз, но нижний слой зависит от HTTP-деталей.
2. **Стрелки вбок.** `SubmissionService` читает задание через чужой `AssignmentRepository`, минуя `AssignmentService`. `AiCheckService` так же использует `SubmissionRepository`. Это связывает модули через устройство хранения данных.
3. **Цикл пакетов `user` ↔ `security`.** `user/BlockedUserInterceptor` импортирует `security/PlatformUserDetails`, а тот импортирует `user/User`. Других циклов между пакетами скан не нашёл.
4. **Сущности выше сервиса.** `Submission` и `User` доходят до контроллера. Стрелка идёт вниз, но через слой: изменение сущности может затронуть контроллеры и представления.

Событие `SubmissionCreatedEvent` отклонением не считаю. Управление идёт от `submission` к `aicheck`, а зависимость в коде обратная: `aicheck` импортирует `submission`. Поэтому модуль сдач ничего не знает об ИИ-проверке, а её сбой не отменяет сдачу.

### Где провёл бы границу иначе

Главная правка — **вынести HTTP из `SubmissionService`**: контроллер превращает `MultipartFile` в нейтральный тип (например, имя, content type, размер и `InputStream`), а сервис получает уже его. Тогда сервис перестанет зависеть от `org.springframework.web`.



### Зачем нужна граница

**Чтобы правила сдачи жили в одном месте и не зависели от способа, которым пришёл запрос и хранятся данные.**

---

## Часть 2. PetClinic: (через агента)

### Модель: Claude Code | Opus 5.5

### Слои

| Слой | Классы | Роль |
|---|---|---|
| Контроллер | `owner/VisitController` | HTTP, загрузка данных, проверка даты, выбор страницы |
| Сервис | **нет** | В `src/main/java` нет ни одного класса `*Service` и ни одной аннотации `@Service` |
| Репозиторий | `owner/OwnerRepository` | Доступ к БД; отдельного `VisitRepository` нет |
| Сущности | `owner/Owner`, `owner/Pet`, `owner/Visit`, база в `model/` | Данные, агрегат `Owner` → `Pet` → `Visit`, каскадное сохранение |
| Представление | `templates/pets/createOrUpdateVisitForm.html` | Форма визита |

### Цепочка вызовов

Перед каждым методом-обработчиком Spring MVC вызывает `@ModelAttribute`-методы:

```
VisitController.loadPetWithVisit
  → OwnerRepository.findById
  → Owner.getPet(Integer)
  → Pet.addVisit (новый пустой Visit)
```

Открытие формы, `GET /owners/{ownerId}/pets/{petId}/visits/new`:

```
VisitController.initNewVisitForm → шаблон pets/createOrUpdateVisitForm
```

Сохранение, `POST` на тот же адрес:

```
VisitController.processNewVisitForm
  → проверка @Valid (Visit: @NotBlank, @Size) и даты визита (должна быть позже сегодняшней)
  → при ошибке: возврат к форме, без сохранения
  → Owner.addVisit → Owner.getPet(Integer) → Pet.addVisit
  → OwnerRepository.save
      → каскад CascadeType.ALL: Owner.pets → Pet.visits
      → INSERT в таблицу visits (выполняет JPA)
  → redirect:/owners/{ownerId}
```

`Pet.addVisit` вызывается дважды с одним и тем же объектом, но `visits` — это `Set`, поэтому дубля нет.

### Все ли стрелки идут «вниз»?

**Да, вверх стрелок нет,** но одного слоя не хватает: контроллер сразу обращается к репозиторию. Пакеты `owner` и `vet` зависят только от `model`, а `model` — ни от кого из них.

Особенности:

- правило «дата визита позже сегодняшней» находится в контроллере, поэтому при другом входе (например, REST) его пришлось бы повторять;
- `Visit` одновременно служит сущностью БД и объектом формы, поэтому на нём есть `@DateTimeFormat` и правила валидации;
- визит сохраняется только через `OwnerRepository.save(owner)`. Это соответствует агрегату, но ради одной записи загружается и сохраняется весь `Owner`.

### Где провёл бы границу иначе

Для учебного CRUD прямой вызов репозитория из контроллера приемлем. Если появится второй вход или новые правила, добавил бы `VisitService.bookVisit(ownerId, petId, visit)` и перенёс бы туда поиск владельца и питомца, проверку даты и сохранение. `@Transactional` тоже стоит поставить на этот метод.

### Зачем нужна граница

**Чтобы бизнес-правило визита можно было менять и проверять без HTTP, форм и шаблонов.**

---

