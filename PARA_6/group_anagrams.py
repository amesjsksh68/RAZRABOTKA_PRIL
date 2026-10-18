from collections import defaultdict
from typing import List


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        groups = defaultdict(list)
        for word in strs:
            count = [0] * 26
            for ch in word:
                count[ord(ch) - ord('a')] += 1
            # список нельзя сделать ключом словаря — переводим в tuple
            groups[tuple(count)].append(word)
        return list(groups.values())


if __name__ == '__main__':
    sol = Solution()

    def normalize(groups):
        return sorted(sorted(g) for g in groups)

    assert normalize(sol.groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])) == \
        normalize([["bat"], ["nat", "tan"], ["ate", "eat", "tea"]])
    assert normalize(sol.groupAnagrams([""])) == [[""]]
    assert normalize(sol.groupAnagrams(["a"])) == [["a"]]
    print(sol.groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    print("All tests passed")

# Вывод:
#   Время O(n * k), где n — число слов, k — максимальная длина слова
#   (частотный словарь из 26 букв строится за O(k), вставка в HashMap — O(1) в среднем).
#   Память O(n * k).
#   Почему HashMap: у анаграмм одинаковый частотный словарь букв — его и делаем ключом,
#   тогда все анаграммы попадают в одну корзину за один проход.