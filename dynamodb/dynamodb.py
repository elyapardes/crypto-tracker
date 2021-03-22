import boto3
import time
import json
from fetcher.ddb_helpers import load_to_dynamodb

# Get the service resource.
dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamodb-local:8000')


# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='bitfinex_pair_prices',
    KeySchema=[
        {
            'AttributeName': 'pair',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'ts',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'pair',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'ts',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='bitfinex_pair_prices')

# Print out some data about the table.
print("Currently, there are " + str(table.item_count) + " rows in the table.")
print("Seeding with a few minutes of data (may be older than 24 hours depending on when this is run...)")

with open('../fixtures/bitfinex_prices/4min_of_bitfinex_prices_fixed.json') as f:
    data = json.load(f)


load_to_dynamodb(table, data)




time.sleep(2)
response = table.get_item( Key = {'pair': 'ethusd', 'ts': "2021-03-19T18:24:30.082044"} )
print(response)

