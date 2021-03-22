import statistics
from . import ddb_controller as db


def compute_std(sample):

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