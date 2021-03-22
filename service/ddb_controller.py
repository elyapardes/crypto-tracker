import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb', endpoint_url="http://dynamodb-local:8000", region_name='local')
table = dynamodb.Table('bitfinex_pair_prices')

def query_pair_all(pair):

    table = dynamodb.Table('bitfinex_pair_prices')
    response = table.query(
        KeyConditionExpression=Key('pair').eq(pair)
    )
    return response['Items']


def query_pair_last_day(pair):

    table = dynamodb.Table('bitfinex_pair_prices')
    response = table.query(
        # Limit=1,
        # ScanIndexForward=False,
        KeyConditionExpression=Key('pair').eq(pair) & Key('ts').gt('2021-03-19T18:25:30.626912')
    )

    return response['Items']


def query_pair_latest(pair):

    table = dynamodb.Table('bitfinex_pair_prices')
    response = table.query(
        Limit=1,
        ScanIndexForward=False,
        KeyConditionExpression=Key('pair').eq(pair)
    )
    return response['Items']