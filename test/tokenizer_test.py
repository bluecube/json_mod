import json_mod.tokenize
import io
from nose.tools import *

def assert_iterables_equal(it1, it2):
    it1 = iter(it1)
    it2 = iter(it2)

    for i, (a, b) in enumerate(zip(it1, it2)):
        assert_equal(a, b, "item {}".format(i))

    with assert_raises(StopIteration):
        next(it1)

    with assert_raises(StopIteration):
        next(it2)

def simple_test():
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('abcd { , [\ntrue "xyz"\n\n\n7 /* this is a comment\n! */ a'),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'abcd'),
                            ('{', json_mod.tokenize.Position(None, 1, 6)),
                            (',', json_mod.tokenize.Position(None, 1, 8)),
                            ('[', json_mod.tokenize.Position(None, 1, 10)),
                            (True, json_mod.tokenize.Position(None, 2, 1)),
                            ('string', json_mod.tokenize.Position(None, 2, 6), 'xyz'),
                            ('number', json_mod.tokenize.Position(None, 5, 1), 7),
                            ('identifier', json_mod.tokenize.Position(None, 6, 6), 'a')])

def unexpected_character_test():
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('abc def @'))

def identifier_test():
    data = 'simple'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'simple')])
    data = '_underscore'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), '_underscore')])
    data = 'underscore_inside'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'underscore_inside')])
    data = 'number4inside'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'number4inside')])
    data = 'interrupting:'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'interrupting'),
                            (':', json_mod.tokenize.Position(None, 1, 13))])
    data = '_ever42ythi_ng:i_s124'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), '_ever42ythi_ng'),
                            (':', json_mod.tokenize.Position(None, 1, 15)),
                            ('identifier', json_mod.tokenize.Position(None, 1, 16), 'i_s124')])

def known_identifier_test():
    data = 'true'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [(True, json_mod.tokenize.Position(None, 1, 1))])
    data = 'false'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [(False, json_mod.tokenize.Position(None, 1, 1))])
    data = 'null'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [(None, json_mod.tokenize.Position(None, 1, 1))])

def python_style_comment_test():
    data = 'a #simple\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a#simple\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a #simple###\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a #\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a # */\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a # //\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])

def one_line_comment_test():
    data = 'a //simple\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a//simple\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a //\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a ///\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a ////\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a //*\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a //#\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])
    data = 'a //*/\na'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 1), 'a')])

def block_comment_test():
    data = 'a /* simple */ a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 16), 'a')])
    data = 'a/* simple */a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 14), 'a')])
    data = 'a/* # */a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 9), 'a')])
    data = 'a/* // */a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 10), 'a')])
    data = 'a/*/**/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 8), 'a')])
    data = 'a/*/*/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 7), 'a')])
    data = 'a/* */a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 7), 'a')])
    data = 'a/**/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 6), 'a')])
    data = 'a/***/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 7), 'a')])
    data = 'a/*\n*/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 3), 'a')])
    data = 'a/**\n/*/a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('identifier', json_mod.tokenize.Position(None, 2, 4), 'a')])

def invalid_comment_test():
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a/a'))

    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a/ * */'))

    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a/*'))

    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a/*/a'))

    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a/'))

def quoted_string_test():
    data = 'a "simple" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), 'simple'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 12), 'a')])
    data = 'a"simple"a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 2), 'simple'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 10), 'a')])
    data = 'a "" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), ''),
                            ('identifier', json_mod.tokenize.Position(None, 1, 6), 'a')])
    data = r'a "\n" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), '\n'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\\" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), '\\'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\"" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), '"'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\u0040" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), '@'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 12), 'a')])
    data = r'a "\u0041\u0042\n\u00e1\u011b" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), 'AB\náě'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 32), 'a')])
    data = r'a """" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), ''),
                            ('string', json_mod.tokenize.Position(None, 1, 5), ''),
                            ('identifier', json_mod.tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\"""\"" a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'a'),
                            ('string', json_mod.tokenize.Position(None, 1, 3), '"'),
                            ('string', json_mod.tokenize.Position(None, 1, 7), '"'),
                            ('identifier', json_mod.tokenize.Position(None, 1, 12), 'a')])

def invalid_quoted_string_test():
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a "\nb"a'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('a " b'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable(r'a " b \"'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable(r'"\uxyzw"'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable(r'"\u10"'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable(r'"\u10 asdf"'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('"\\'))

def json_number_test():
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0.2'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 0.2)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1.2'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1.2)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1.25'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1.25)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42.5'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42.5)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42.52'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42.52)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('5e0'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 5e0)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1e1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1e1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42E+1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42e+1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1.2e-1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1.2e-1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('2e-10'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 2e-10)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('-42.5'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), -42.5)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('-1.2e-1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), -1.2e-1)])

    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0asdf'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 0),
                            ('identifier', json_mod.tokenize.Position(None, 1, 2), 'asdf')])

def ext_number_test():
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0x1'),
                           [('ext_number', json_mod.tokenize.Position(None, 1, 1), 1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0x10'),
                           [('ext_number', json_mod.tokenize.Position(None, 1, 1), 16)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0b01001'),
                           [('ext_number', json_mod.tokenize.Position(None, 1, 1), 9)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0o21'),
                           [('ext_number', json_mod.tokenize.Position(None, 1, 1), 17)])

def invalid_number_test():
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('0xzzz'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('0b'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('00'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('05'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('0.'))
    with assert_raises(ValueError):
        print("asdf")
        list(json_mod.tokenize.tokenize_iterable('0.abc'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('1E'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('1Easdf'))
    with assert_raises(ValueError):
        list(json_mod.tokenize.tokenize_iterable('1E+asdf'))

def position_str_test():
    assert_equal(str(json_mod.tokenize.Position("X", 1, 2)), "X, line 1, column 2")
    assert_equal(str(json_mod.tokenize.Position(None, 1, 2)), "line 1, column 2")

def file_positions_test():
    fp = io.StringIO("xy\nXY")
    fp.name = "Z"
    assert_iterables_equal(json_mod.tokenize.positions_file(fp),
                           [('x', json_mod.tokenize.Position("Z", 1, 1)),
                            ('y', json_mod.tokenize.Position("Z", 1, 2)),
                            ('\n', json_mod.tokenize.Position("Z", 1, 3)),
                            ('X', json_mod.tokenize.Position("Z", 2, 1)),
                            ('Y', json_mod.tokenize.Position("Z", 2, 2)),
                            (None, None)])

    fp = io.StringIO("xy\nXY")
    assert_iterables_equal(json_mod.tokenize.positions_file(fp),
                           [('x', json_mod.tokenize.Position(None, 1, 1)),
                            ('y', json_mod.tokenize.Position(None, 1, 2)),
                            ('\n', json_mod.tokenize.Position(None, 1, 3)),
                            ('X', json_mod.tokenize.Position(None, 2, 1)),
                            ('Y', json_mod.tokenize.Position(None, 2, 2)),
                            (None, None)])

def string_positions_test():
    assert_iterables_equal(json_mod.tokenize.positions("xy\nXY"),
                           [('x', json_mod.tokenize.Position(None, 1, 1)),
                            ('y', json_mod.tokenize.Position(None, 1, 2)),
                            ('\n', json_mod.tokenize.Position(None, 1, 3)),
                            ('X', json_mod.tokenize.Position(None, 2, 1)),
                            ('Y', json_mod.tokenize.Position(None, 2, 2)),
                            (None, None)])

def iterable_positions_test():
    def it():
        for c in "xy\nXY":
            yield c

    assert_iterables_equal(json_mod.tokenize.positions(it()),
                           [('x', json_mod.tokenize.Position(None, 1, 1)),
                            ('y', json_mod.tokenize.Position(None, 1, 2)),
                            ('\n', json_mod.tokenize.Position(None, 1, 3)),
                            ('X', json_mod.tokenize.Position(None, 2, 1)),
                            ('Y', json_mod.tokenize.Position(None, 2, 2)),
                            (None, None)])
