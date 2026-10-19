class SolutionBruteForce:
    # Через два цикла. Для каждой буквы s ищем и вычёркиваем такую же в t
    # Время O(n²), память O(n)

    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        rest = list(t)
        for ch in s:
            try:
                rest.pop(rest.index(ch))
            except ValueError:
                return False
        return True


class Solution:
    # Через словарь. Считаем частоты букв. Время O(n), память O(1)

    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        count = {}
        for ch in s:
            count[ch] = count.get(ch, 0) + 1
        for ch in t:
            if count.get(ch, 0) == 0:
                return False
            count[ch] -= 1
        return True


if __name__ == '__main__':
    for sol in (SolutionBruteForce(), Solution()):
        assert sol.isAnagram("anagram", "nagaram") is True
        assert sol.isAnagram("rat", "car") is False
        assert sol.isAnagram("a", "ab") is False
        assert sol.isAnagram("aacc", "ccac") is False
    print("All tests passed")

# Вывод:
#   Через вложенный цикл скорость получается O(n²). Для каждой буквы линейно ищем пару во второй строке
#   Через словарь O(n). Один проход для подсчёта частот и один для их уменьшения
