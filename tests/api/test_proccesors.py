import unittest

import devo.api.processors as processors


class TestApi(unittest.TestCase):

    def setUp(self):
        self.stream_spaces = b'       '
        self.valid_json = b'{"a":1, "b":2, "c":3, "d":4}'
        self.compact_simple = b'{"d":[1506439800000, "self", "email@devo.com",\
            null, 1]}'
        self.names = ['eventdate', 'domain', 'userEmail', 'country', 'count']
        self.simple_names = {
            "m": {
                "eventdate": {
                    "type": "timestamp",
                    "index": 0
                },
                "domain": {
                    "type": "str",
                    "index": 1
                },
                "userEmail": {
                    "type": "str",
                    "index": 2
                },
                "country": {
                    "type": "str",
                    "index": 3
                },
                "count": {
                    "type": "int8",
                    "index": 4
                }
            }
        }
        self.compact_response = b'{ "msg": "", "status": 0, "object": { "m": \
            { "eventdate": { "type": "timestamp", "index": 0 }, "domain": \
            { "type": "str", "index": 1 }, "userEmail": { "type": "str", \
            "index": 2 }, "country": { "type": "str", "index": 3 }, "count": \
            { "type": "int8", "index": 4 } }, "d": [ [ 1506442210000, "self", \
            "luis.xxxxx@devo.com", null, 2 ], [ 1506442220000, "self", \
            "goaquinxxx@gmail.com", null, 2 ] ] }}'

    def test_proc_default(self):
        self.assertEqual(processors.proc_default()(self.stream_spaces), b'')

    def test_proc_json(self):
        self.assertEqual(processors.proc_json()(None), None)
        self.assertEqual(processors.proc_json()(self.stream_spaces), None)
        self.assertEqual(processors.proc_json()(self.valid_json)['b'], 2)

    def test_proc_json_simple(self):
        self.assertEqual(processors.proc_json_simple()(None), None)
        self.assertEqual(processors.proc_json_simple()(self.stream_spaces),
                         None)
        self.assertEqual(processors.proc_json_simple()(self.valid_json)['b'],
                         2)

    def test_proc_json_compact_to_array(self):
        self.assertEqual(processors.proc_json_compact_to_array()(None), None)
        self.assertEqual(
            processors.proc_json_compact_to_array()(self.stream_spaces), None)
        self.assertEqual(
            processors.proc_json_compact_to_array()(self.compact_response),
            [[1506442210000, 'self', 'luis.xxxxx@devo.com', None, 2],
             [1506442220000, 'self', 'goaquinxxx@gmail.com', None, 2]])

    def test_json_compact_simple_names(self):
        self.assertEqual(
            processors.json_compact_simple_names(self.stream_spaces), [])
        self.assertEqual(
            processors.json_compact_simple_names(self.simple_names['m']),
            ['eventdate', 'domain', 'userEmail', 'country', 'count'])

    def test_proc_json_compact_simple_to_jobj(self):
        self.assertEqual(
            processors.proc_json_compact_simple_to_jobj(self.names)(
                self.stream_spaces), {})
        self.assertEqual(
            processors.proc_json_compact_simple_to_jobj(self.names)(
                self.compact_simple), {
                    'eventdate': 1506439800000,
                    'domain': 'self',
                    'userEmail': 'email@devo.com',
                    'country': None,
                    'count': 1
                })

    def test_proc_json_compact_simple_to_array(self):
        self.assertEqual(
            processors.proc_json_compact_simple_to_array()(self.stream_spaces),
            [])
        self.assertEqual(
            processors.proc_json_compact_simple_to_array()(
                self.compact_simple),
            [1506439800000, "self", "email@devo.com", None, 1])


if __name__ == '__main__':
    unittest.main()
