import boto3
from boto3.dynamodb.conditions import Key


def query_pair(pair, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('bitfinex_pair_prices')
    response = table.query(
        KeyConditionExpression=Key('pair').eq(pair)
    )
    return response['Items']


def query_pair_latest_price(pair, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('bitfinex_pair_prices')
    response = table.query(
        Limit=1,
        ScanIndexForward=False,
        KeyConditionExpression=Key('pair').eq(pair)
    )
    return response['Items']


def load_to_dynamodb(table, data):
    print("Loading prices to DynamoDB")
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(
                Item={
                    'pair': item['pair'],
                    'ts': item['ts'],
                    'price': str(item['price'])
                }
            )
    print("Successfully loaded prices to DynamoDB!")


if __name__ == '__main__':
    pair = 'ethusd'
    print(f"Prices for {pair}")
    # prices = query_pair(pair)
    prices = query_pair_latest_price(pair)
    for price in prices:
        print(price['ts'], ":", price['price'])