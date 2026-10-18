class Solution:
    def isValid(self, s: str) -> bool:
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []
        for ch in s:
            if ch in pairs:
                if not stack or stack.pop() != pairs[ch]:
                    return False
            else:
                stack.append(ch)
        return not stack


if __name__ == '__main__':
    sol = Solution()
    tests = {
        "()": True,
        "()[]{}": True,
        "(]": False,
        "([])": True,
        "([)]": False,
        "{[]}": True,
        "(": False,
        ")": False,
        "": True,
    }
    for s, expected in tests.items():
        result = sol.isValid(s)
        assert result == expected, f"{s!r}: got {result}, expected {expected}"
        print(f"{s!r:10} -> {result}")
    print("All tests passed")

# Вывод:
#   Время O(n) — один проход по строке, push/pop стека за O(1); память O(n) в худшем случае.
#   Почему стек: закрывающая скобка всегда относится к ПОСЛЕДНЕЙ ещё не закрытой
#   открывающей — это LIFO, ровно то, что даёт стек.



