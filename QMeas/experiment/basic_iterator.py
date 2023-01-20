class Counter:
    def __init__(self, n, index=''):
        self.n = n
        self.index = index
        self.linespace = range(n)

    def __getitem__(self, key):
        return self.linespace[key]

    def __str__(self):
        return f'L{self.n}{self.index}'


if __name__ == '__main__':
    for c in Counter(5):
        print(c)
