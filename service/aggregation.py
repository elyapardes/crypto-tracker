import statistics
from . import ddb_controller as db


def compute_std(sample):
    """
    Computes standard deviation of list of values.
    A possible optimization could be to do incremental calculation, though I haven't researched this yet:
    https://math.stackexchange.com/questions/102978/incremental-computation-of-standard-deviation

    """
    # sample = [1, 2, 3, 4, 5]

    res = statistics.stdev(sample)
    return res


def rank_stds(pair_stds):
    stds = []
    for pair in pair_stds:
        # print('  current pair is ' + pair)
        prices = db.query_pair_last_day(pair)
        # print(prices)
        std = compute_std([float(item['price']) for item in prices])
        stds.append({
            'pair': pair,
            'prices': prices,  # TODO clean up json hierarchy
            'std': std
        })
    # return in descending order
    return sorted(stds, key=lambda x: x['std'], reverse=True)