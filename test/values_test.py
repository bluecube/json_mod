import json_mod
from nose.tools import *

def test():
    assert_equal(json_mod.loads('["abcd", defg]'),
                 ["abcd", "defg"])
    assert_equal(json_mod.loads('{"abcd": 12, lmnop: 0x101010}'),
                 {"abcd": 12, "lmnop": 0x101010})
    assert_equal(json_mod.loads('{"abcd": 12, lmnop: 0x101010}'),
                 {"abcd": 12, "lmnop": 0x101010})
    assert_equal(json_mod.loads('{"123": #asdf\n[null, true, false], "456" /*: true : */ :false,}'),
                 {"123": [None, True, False], "456": False})
    assert_equal(json_mod.loads('[[[[[[[[[[[[[[[[{a: b, c:d}]]]]]]]]]]]]]]]]'),
                 [[[[[[[[[[[[[[[[{"a": "b", "c":"d"}]]]]]]]]]]]]]]]])
    assert_equal(json_mod.loads('[_]'),
                 ["_"])
    assert_equal(json_mod.loads('[1.562e-3]'),
                 [1.562e-3])
