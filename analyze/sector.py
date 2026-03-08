from collections import Counter


def get_hot_sectors(stocks):

    sectors = []

    for s in stocks:

        if "hybk" in s:
            sectors.append(s["hybk"])

    counter = Counter(sectors)

    return counter.most_common(3)
