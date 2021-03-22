import flask
from flask import request, jsonify
from datetime import datetime
# from aggregation import compute_std
from . import aggregation as agg
# from .aggregation import compute_std
from . import ddb_controller as db
# import ddb_controller as db

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some tests data for our catalog in the form of a list of dictionaries.
pairs = [
    {'pair': 'btcusd', 'ts': datetime(2019, 5, 18, 15, 17, 8, 123455), 'price': 56000.0},
    {'pair': 'btceth', 'ts': datetime(2019, 5, 18, 15, 17, 8, 155555), 'price': 3.1},
    {'pair': 'nmreth', 'ts': datetime(2019, 5, 18, 15, 17, 8, 245677), 'price': 0.001},
    {'pair': 'btcusd', 'ts': datetime(2019, 5, 18, 15, 17, 9, 123455), 'price': 56600.0},
    {'pair': 'btceth', 'ts': datetime(2019, 5, 18, 15, 17, 9, 155555), 'price': 3.3},
    {'pair': 'nmreth', 'ts': datetime(2019, 5, 18, 15, 17, 9, 245677), 'price': 0.002}
]

api_path = '/service/v1'


def get_pair_data(pair): # TODO replace
    results = []
    for pair_dict in pairs:
        if pair_dict['pair'] == pair:
            results.append(pair_dict['price'])
    return results


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome!</h1>
<p>This is an API for cryptocurrencies data.</p>'''


@app.route(api_path + '/pairs/all', methods=['GET'])
def api_all():
    return jsonify(pairs)


@app.route(api_path + '/pair/<pair>', methods=['GET'])
def api_id(pair):
    # app.logger.info(pair)
    results = db.query_pair_latest(pair)


    return jsonify(results)


@app.route(api_path + '/pair_last_day/<pair>', methods=['GET'])
def get_latest_day_prices_for_pair(pair):

    results = db.query_pair_last_day(pair)

    return jsonify(results)


@app.route(api_path + '/std/<pair>', methods=['GET'])
def get_pair_std(pair):
    prices = db.query_pair_all(pair)
    # TODO figure out how to use float with dynamo, for now converting back and forth
    return jsonify({
        'pair': pair,
        'std': agg.compute_std([float(item['price']) for item in prices])
    })


@app.route(api_path + '/rank', methods=['GET'])
def get_ranked_stds():
    # eg: http://127.0.0.1:5000/api/v1/rank?pair=btcusd&pair=ethusd&pair=daiusd

    pairs = request.args.getlist('pair', type=str)

    print('pairs:')
    print(pairs)
    ranked_stds = agg.rank_stds(pairs)
    print('stds')
    print(ranked_stds)
    return jsonify(ranked_stds)

if __name__=='__main__':
    app.run(host='0.0.0.0')
