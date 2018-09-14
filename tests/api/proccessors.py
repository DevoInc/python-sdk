# -*- coding: utf-8 -*-
import unittest
import sys
from devo.api.proccessors import *

PY3 = sys.version_info[0] > 2


class TestEngine(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestEngine, self).__init__(*args, **kwargs)
        self.setUp()

    def test_default_proc(self):
        self.assertIsInstance(proc_default(self.djson), dict)
        self.assertIsNone(proc_default(""))

    def test_proc_json(self):
        data = proc_json(self.procjsonmulti)
        test = proc_default(self.djson)

        if PY3:
            self.assertIsInstance(data, map)
        else:
            self.assertIsInstance(data, list)

        i = 0
        for item in data:
            self.assertDictEqual(item, test['object'][i])
            i += 1

    def setUp(self):
        self.djson = '{"success": true, "status": 0, "msg": "valid request", ' \
                     '"object": [ ' \
                     '{ ' \
                             '"eventdate": "2016-10-24 06:35:00.000",' \
                             '"host": "aws-apiodata-euw1-52-49-216-97",' \
                             '"memory_heap_used": "3.049341704E9",' \
                             '"memory_non_heap_used": "1.21090632E8"' \
                     '},{' \
                             '"eventdate": "2016-10-24 06:36:00.000",' \
                             '"host": "aws-apiodata-euw1-52-49-216-97",' \
                             '"memory_heap_used": "3.04991028E9",' \
                             '"memory_non_heap_used": "1.21090632E8"' \
                     '}]}'

        self.procjsonmulti = '{"eventdate": "2016-10-24 06:35:00.000",' \
                             '"host": "aws-apiodata-euw1-52-49-216-97",' \
                             '"memory_heap_used": "3.049341704E9",' \
                             '"memory_non_heap_used": "1.21090632E8"}\r\n ' \
                             '{"eventdate": "2016-10-24 06:36:00.000",' \
                             '"host": "aws-apiodata-euw1-52-49-216-97",' \
                             '"memory_heap_used": "3.04991028E9",' \
                             '"memory_non_heap_used": "1.21090632E8"}'


if __name__ == '__main__':
    unittest.main()

