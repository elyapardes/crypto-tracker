import aiohttp
import asyncio
from datetime import datetime



class CryptoPriceFetcher:
    """
    Fetches prices for each individual currency pair (using only bitfinex)
    Asyncio is used as this is network/IO bound.
    """

    def __init__(self, base_url, pairs):
        self.base_url = base_url
        self.pairs = pairs


    async def get_individual_price(self, session, pair, pair_url):
        async with session.get(pair_url) as response:
            json_response = await response.json()
            print(json_response)

            return { # TODO currently using now as timestamp, would be more accurate to have ts defined in data source
                'ts': datetime.now().isoformat(),
                'pair': pair,
                'price': json_response['result']['price']
            }

    async def get_prices(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_individual_price(session, pair, self.base_url + pair + '/price')
                     for pair in self.pairs]
            results = await asyncio.gather(*tasks)
            return results
