import time
import asyncio
from fetcher.data_fetchers import CryptoPriceFetcher
from fetcher.ddb_helpers import load_to_dynamodb
import json
import random
import boto3


# @timer(1, 1)
def run_async(pairs):
    """
    Instantiates and runs fetcher which makes the requests to get prices for all currency pairs.
    The requests are made using asyncio to optimize IO (network)-heavy tasks.

    :param pairs: List of currency pairs, eg. ["btcusd", "ethusd"]
    :return: res: List of dicts containing price data
    """
    # url = "https://jsonplaceholder.typicode.com/posts/" # TODO swap url
    url = "https://api.cryptowat.ch/markets/bitfinex/"  # :pair/price
    fetcher = CryptoPriceFetcher(url, pairs)
    res = asyncio.run(fetcher.get_prices())
    print(f"Successfully fetched {str(len(res))} prices")
    # with open('fixtures/bitfinex_prices/bitfinex_prices_nogood_' + str(random.randrange(1000)) + '.txt', 'w') as outfile:
    #     json.dump(res, outfile)
    return res


if __name__ == '__main__':

    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000", region_name='local')
    table = dynamodb.Table('bitfinex_pair_prices')

    # using flat file for now as a list of currency pairs for each exchange
    with open('fetcher/markets.json') as f:
        data = json.load(f)

    cnter = 0
    pairs_for_bitfinex = []
    for market_pair in data['result']:
        # focusing on bitfinex for now, and ignoring perpetual-future-inverse (didn't have a chance to look into what that is)
        if market_pair['exchange'] != 'bitfinex' or 'perpetual-future-inverse' in market_pair['pair']:
            continue
        pairs_for_bitfinex.append(market_pair['pair'])
        cnter += 1
        # Can be used to reduce allowance usage
        if cnter==2:
            break

    for i in range(0, 500):
        res = run_async(pairs_for_bitfinex)
        load_to_dynamodb(table, res)
        # Simple mechanism to get data for every minute.
        # We'd probably want to use something more rubust such as run run_async as part of an Airflow DAG
        time.sleep(60)





