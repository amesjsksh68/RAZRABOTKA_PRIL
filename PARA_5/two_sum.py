import random
import time
from typing import List


class SolutionBruteForce:
    # Через два цикла. Время O(n²), память O(1)

    def twoSum(self, nums: List[int], target: int) -> List[int]:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []


class Solution:
    # Через словарь. Время O(n), память O(n)

    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(nums):
            need = target - num
            if need in seen:
                return [seen[need], i]
            seen[num] = i
        return []


if __name__ == '__main__':
    for sol in (SolutionBruteForce(), Solution()):
        assert sorted(sol.twoSum([2, 7, 11, 15], 9)) == [0, 1]
        assert sorted(sol.twoSum([3, 2, 4], 6)) == [1, 2]
        assert sorted(sol.twoSum([3, 3], 6)) == [0, 1]
        assert sorted(sol.twoSum([-1, -2, -3, -4, -5], -8)) == [2, 4]
    print("All tests passed")

    n = 5000
    nums = random.sample(range(1, 10 ** 9), n - 2) + [-1, -2]
    target = -3
    for sol in (SolutionBruteForce(), Solution()):
        start = time.perf_counter()
        sol.twoSum(nums, target)
        print(f"{type(sol).__name__:20} n={n}: {(time.perf_counter() - start) * 1000:.2f} ms")


# Вывод:
#   HashMap выигрывает, потому что вместо внутреннего цикла по всем остальным числам
#   делает один поиск в хеш-таблице за O(1). В итоге вместо O(n²) получается O(n)
#   Из минусов это дополнительные расходы на память O(n) под словарь
#   Локальный замер на n=5000: через двойной цикл ~523.1 ms, HashMap ~0.82 ms
