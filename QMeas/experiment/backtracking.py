from basic_iterator import Counter


def linspacer_iterator(digits):
    res = []

    def backtrack(i):
        if i == len(digits):
            return
        for c in digits[i]:
            res.append(c)
            backtrack(i+1)

    backtrack(0)
    return res


if __name__ == '__main__':
    a, a1 = Counter(1, 'a'), Counter(1, 'b')
    b, b1 = Counter(2, 'a'), Counter(2, 'b')
    c, c1 = Counter(3, 'a'), Counter(3, 'b')
    ans = linspacer_iterator([[a, a1], [b, b1], [c, c1]])
    for i in ans:
        print(i, end=' ')
