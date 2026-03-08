from collections import Counter

def get_hot_sectors(stocks):
    sectors = [s.get("hybk") for s in stocks if s.get("hybk")]
    counter = Counter(sectors)
    return counter.most_common(3)
