import unittest
from service.aggregation import rank_stds
from unittest.mock import patch


class TestSTDs(unittest.TestCase):

    @patch('service.ddb_controller.query_pair_last_day')
    def test_get_std_for_several_pairs(self, query_pair_all_mock):
        query_pair_all_mock.side_effect = [
            [
                {'price': 3},
                {'price': 4},
                {'price': 7}
            ],
            [
                {'price': 1},
                {'price': 4},
                {'price': 8}
            ],
            [
                {'price': 200},
                {'price': 240},
                {'price': 270}
            ]
        ]

        stds = rank_stds(['pair1', 'pair2', 'pair3'])
        assert(stds[0]['pair'] == 'pair3')
        assert(stds[1]['pair'] == 'pair2')



if __name__ == '__main__':
    unittest.main()