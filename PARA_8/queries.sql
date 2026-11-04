-- ДЗ-8: SQL-выборки по схеме StPlatform (SQLite)
-- Источник данных: pair-08-stplatform-demo.sql
-- Запуск: sqlite3 stplatform.db < pair-08-stplatform-demo.sql
--         sqlite3 stplatform.db < queries.sql


-- (a) Все сдачи студента по фамилии (JOIN)
-- Что делает: соединяет сдачи с их авторами и заданиями и выводит все сдачи
-- студента с фамилией «Иванов» (с названием задания, статусом и датой).
-- Пробел в 'Иванов %' нужен, чтобы не захватить «Иванову Марию».
SELECT u.full_name,
       a.pair_number,
       a.title       AS assignment,
       s.link,
       s.status,
       s.created_at
FROM submissions s
JOIN users      u ON u.id = s.student_id
JOIN assignment a ON a.id = s.assignment_id
WHERE u.full_name LIKE 'Иванов %'
ORDER BY s.created_at;


-- (b) Сколько сдач пришло на каждое задание (JOIN + COUNT + GROUP BY)
-- Что делает: группирует сдачи по заданиям и считает их количество
-- (и число разных студентов), показывая и задания без единой сдачи с нулём.
-- LEFT JOIN + COUNT(s.id), а не COUNT(*): иначе задание пары 8 пропало бы
-- (при INNER JOIN) или получило бы 1 вместо 0.
SELECT a.pair_number,
       a.title,
       COUNT(s.id)                  AS submissions_count,
       COUNT(DISTINCT s.student_id) AS students_count
FROM assignment a
LEFT JOIN submissions s ON s.assignment_id = a.id
GROUP BY a.id, a.pair_number, a.title
ORDER BY a.pair_number;


-- (c) Студенты, не сдавшие ни одной работы — «кого пинать»
-- Что делает: берёт всех пользователей с ролью STUDENT и оставляет только тех,
-- у кого в submissions нет ни одной строки (преподаватель сюда не попадает).
SELECT u.full_name, u.group_name, u.telegram
FROM users u
LEFT JOIN submissions s ON s.student_id = u.id
WHERE u.role = 'STUDENT'
  AND s.id IS NULL
ORDER BY u.group_name, u.full_name;

-- то же самое через NOT EXISTS:
-- SELECT u.full_name, u.group_name, u.telegram
-- FROM users u
-- WHERE u.role = 'STUDENT'
--   AND NOT EXISTS (SELECT 1 FROM submissions s WHERE s.student_id = u.id);
