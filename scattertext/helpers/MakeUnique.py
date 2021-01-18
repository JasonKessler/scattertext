from collections import Counter


def make_unique(lst, sep='-'):
    seen = Counter()
    out = []
    counts = Counter(lst)
    for el in lst:
        out.append(el + ('' if counts[el] == 1 else sep + str(seen[el] + 1)))
        seen[el] += 1
    return out
