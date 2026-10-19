from typing import List


class SolutionBruteForce:
    # Через вложенный цикл. Сравниваем каждую пару. Время O(n²), память O(1)
    # На питоне при n до 10^5 на LeetCode иногда получался Time Limit Exceeded

    def containsDuplicate(self, nums: List[int]) -> bool:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] == nums[j]:
                    return True
        return False


class Solution:
    # Через словарь. Запоминаем увиденные числа. Время O(n), память O(n)

    def containsDuplicate(self, nums: List[int]) -> bool:
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False


if __name__ == '__main__':
    for sol in (SolutionBruteForce(), Solution()):
        assert sol.containsDuplicate([1, 2, 3, 1]) is True
        assert sol.containsDuplicate([1, 2, 3, 4]) is False
        assert sol.containsDuplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2]) is True
        assert sol.containsDuplicate([1]) is False
    print("All tests passed")

# Вывод:
#   Через вложенный цикл скорость получается O(n²). Для каждого числа просматриваем все следующие
#   Через словарь O(n). Проверка на наличие ключа за O(1) в среднем -> один проход по массиву.
