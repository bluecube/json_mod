import json_mod.tokenize as tokenize
import io
from nose.tools import *

def tokenize_iterable(string):
    characters = tokenize.positions(string)
    return list(tokenize.tokenize(characters, True))

def simple_test():
    assert_equal(tokenize_iterable('abcd { , [\ntrue "xyz"\n\n\n7 /* this is a comment\n! */ a'),
                 [('identifier', tokenize.Position(None, 1, 1), 'abcd'),
                  ('{', tokenize.Position(None, 1, 6)),
                  (',', tokenize.Position(None, 1, 8)),
                  ('[', tokenize.Position(None, 1, 10)),
                  (True, tokenize.Position(None, 2, 1)),
                  ('string', tokenize.Position(None, 2, 6), 'xyz'),
                  ('number', tokenize.Position(None, 5, 1), 7),
                  ('identifier', tokenize.Position(None, 6, 6), 'a'),])

def unexpected_character_test():
    with assert_raises(ValueError):
        list(tokenize_iterable('abc def @'))

def identifier_test():
    data = 'simple'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'simple')])
    data = '_underscore'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), '_underscore')])
    data = 'underscore_inside'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'underscore_inside')])
    data = 'number4inside'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'number4inside')])
    data = 'interrupting:'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'interrupting'),
                  (':', tokenize.Position(None, 1, 13))])
    data = '_ever42ythi_ng:i_s124'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), '_ever42ythi_ng'),
                  (':', tokenize.Position(None, 1, 15)),
                  ('identifier', tokenize.Position(None, 1, 16), 'i_s124')])

def known_identifier_test():
    data = 'true'
    assert_equal(tokenize_iterable(data),
                 [(True, tokenize.Position(None, 1, 1))])
    data = 'false'
    assert_equal(tokenize_iterable(data),
                 [(False, tokenize.Position(None, 1, 1))])
    data = 'null'
    assert_equal(tokenize_iterable(data),
                 [(None, tokenize.Position(None, 1, 1))])

def python_style_comment_test():
    data = 'a #simple\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a#simple\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a #simple###\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a #\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a # */\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a # //\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])

def one_line_comment_test():
    data = 'a //simple\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a//simple\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a //\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a ///\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a ////\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a //*\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a //#\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])
    data = 'a //*/\na'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 1), 'a')])

def block_comment_test():
    data = 'a /* simple */ a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 16), 'a')])
    data = 'a/* simple */a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 14), 'a')])
    data = 'a/* # */a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 9), 'a')])
    data = 'a/* // */a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 10), 'a')])
    data = 'a/*/**/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 8), 'a')])
    data = 'a/*/*/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 7), 'a')])
    data = 'a/* */a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 7), 'a')])
    data = 'a/**/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 6), 'a')])
    data = 'a/***/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 1, 7), 'a')])
    data = 'a/*\n*/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 3), 'a')])
    data = 'a/**\n/*/a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('identifier', tokenize.Position(None, 2, 4), 'a')])

def invalid_comment_test():
    with assert_raises(ValueError):
        list(tokenize_iterable('a/a'))

    with assert_raises(ValueError):
        list(tokenize_iterable('a/ * */'))

    with assert_raises(ValueError):
        list(tokenize_iterable('a/*'))

    with assert_raises(ValueError):
        list(tokenize_iterable('a/*/a'))

    with assert_raises(ValueError):
        list(tokenize_iterable('a/'))

def quoted_string_test():
    data = 'a "simple" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), 'simple'),
                  ('identifier', tokenize.Position(None, 1, 12), 'a')])
    data = 'a"simple"a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 2), 'simple'),
                  ('identifier', tokenize.Position(None, 1, 10), 'a')])
    data = 'a "" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), ''),
                  ('identifier', tokenize.Position(None, 1, 6), 'a')])
    data = r'a "\n" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), '\n'),
                  ('identifier', tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\\" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), '\\'),
                  ('identifier', tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\"" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), '"'),
                  ('identifier', tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\u0040" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), '@'),
                  ('identifier', tokenize.Position(None, 1, 12), 'a')])
    data = r'a "\u0041\u0042\n\u00e1\u011b" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), 'AB\náě'),
                  ('identifier', tokenize.Position(None, 1, 32), 'a')])
    data = r'a """" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), ''),
                  ('string', tokenize.Position(None, 1, 5), ''),
                  ('identifier', tokenize.Position(None, 1, 8), 'a')])
    data = r'a "\"""\"" a'
    assert_equal(tokenize_iterable(data),
                 [('identifier', tokenize.Position(None, 1, 1), 'a'),
                  ('string', tokenize.Position(None, 1, 3), '"'),
                  ('string', tokenize.Position(None, 1, 7), '"'),
                  ('identifier', tokenize.Position(None, 1, 12), 'a')])

def invalid_quoted_string_test():
    with assert_raises(ValueError):
        list(tokenize_iterable('a "\nb"a'))
    with assert_raises(ValueError):
        list(tokenize_iterable('a " b'))
    with assert_raises(ValueError):
        list(tokenize_iterable(r'a " b \"'))
    with assert_raises(ValueError):
        list(tokenize_iterable(r'"\uxyzw"'))
    with assert_raises(ValueError):
        list(tokenize_iterable(r'"\u10"'))
    with assert_raises(ValueError):
        list(tokenize_iterable(r'"\u10 asdf"'))
    with assert_raises(ValueError):
        list(tokenize_iterable('"\\'))
    with assert_raises(ValueError):
        list(tokenize_iterable('"	"'))
    with assert_raises(ValueError):
        list(tokenize_iterable('"\u0000"'))

def json_number_test():
    assert_equal(tokenize_iterable('1'),
                 [('number', tokenize.Position(None, 1, 1), 1)])
    assert_equal(tokenize_iterable('42'),
                 [('number', tokenize.Position(None, 1, 1), 42)])
    assert_equal(tokenize_iterable('0.2'),
                 [('number', tokenize.Position(None, 1, 1), 0.2)])
    assert_equal(tokenize_iterable('1.2'),
                 [('number', tokenize.Position(None, 1, 1), 1.2)])
    assert_equal(tokenize_iterable('1.25'),
                 [('number', tokenize.Position(None, 1, 1), 1.25)])
    assert_equal(tokenize_iterable('42.5'),
                 [('number', tokenize.Position(None, 1, 1), 42.5)])
    assert_equal(tokenize_iterable('42.52'),
                 [('number', tokenize.Position(None, 1, 1), 42.52)])
    assert_equal(tokenize_iterable('5e0'),
                 [('number', tokenize.Position(None, 1, 1), 5e0)])
    assert_equal(tokenize_iterable('1e1'),
                 [('number', tokenize.Position(None, 1, 1), 1e1)])
    assert_equal(tokenize_iterable('42E+1'),
                 [('number', tokenize.Position(None, 1, 1), 42e+1)])
    assert_equal(tokenize_iterable('1.2e-1'),
                 [('number', tokenize.Position(None, 1, 1), 1.2e-1)])
    assert_equal(tokenize_iterable('2e-10'),
                 [('number', tokenize.Position(None, 1, 1), 2e-10)])
    assert_equal(tokenize_iterable('-42.5'),
                 [('number', tokenize.Position(None, 1, 1), -42.5)])
    assert_equal(tokenize_iterable('-1.2e-1'),
                 [('number', tokenize.Position(None, 1, 1), -1.2e-1)])

    assert_equal(tokenize_iterable('0asdf'),
                 [('number', tokenize.Position(None, 1, 1), 0),
                  ('identifier', tokenize.Position(None, 1, 2), 'asdf')])

def ext_number_test():
    assert_equal(tokenize_iterable('0x1'),
                 [('ext_number', tokenize.Position(None, 1, 1), 1)])
    assert_equal(tokenize_iterable('0x10'),
                 [('ext_number', tokenize.Position(None, 1, 1), 16)])
    assert_equal(tokenize_iterable('0b01001'),
                 [('ext_number', tokenize.Position(None, 1, 1), 9)])
    assert_equal(tokenize_iterable('0o21'),
                 [('ext_number', tokenize.Position(None, 1, 1), 17)])

def invalid_number_test():
    with assert_raises(ValueError):
        list(tokenize_iterable('0xzzz'))
    with assert_raises(ValueError):
        list(tokenize_iterable('0b'))
    with assert_raises(ValueError):
        list(tokenize_iterable('00'))
    with assert_raises(ValueError):
        list(tokenize_iterable('05'))
    with assert_raises(ValueError):
        list(tokenize_iterable('0.'))
    with assert_raises(ValueError):
        list(tokenize_iterable('0.abc'))
    with assert_raises(ValueError):
        list(tokenize_iterable('1E'))
    with assert_raises(ValueError):
        list(tokenize_iterable('1Easdf'))
    with assert_raises(ValueError):
        list(tokenize_iterable('1E+asdf'))

def position_str_test():
    assert_equal(str(tokenize.Position("X", 1, 2)), "X, line 1, column 2")
    assert_equal(str(tokenize.Position(None, 1, 2)), "line 1, column 2")

def file_positions_test():
    fp = io.StringIO("xy\nXY")
    fp.name = "Z"
    assert_equal(list(tokenize.positions_file(fp)),
                 [('x', tokenize.Position("Z", 1, 1)),
                  ('y', tokenize.Position("Z", 1, 2)),
                  ('\n', tokenize.Position("Z", 1, 3)),
                  ('X', tokenize.Position("Z", 2, 1)),
                  ('Y', tokenize.Position("Z", 2, 2)),
                  (None, None)])

    fp = io.StringIO("xy\nXY")
    assert_equal(list(tokenize.positions_file(fp)),
                 [('x', tokenize.Position(None, 1, 1)),
                  ('y', tokenize.Position(None, 1, 2)),
                  ('\n', tokenize.Position(None, 1, 3)),
                  ('X', tokenize.Position(None, 2, 1)),
                  ('Y', tokenize.Position(None, 2, 2)),
                  (None, None)])

def string_positions_test():
    assert_equal(list(tokenize.positions("xy\nXY")),
                 [('x', tokenize.Position(None, 1, 1)),
                  ('y', tokenize.Position(None, 1, 2)),
                  ('\n', tokenize.Position(None, 1, 3)),
                  ('X', tokenize.Position(None, 2, 1)),
                  ('Y', tokenize.Position(None, 2, 2)),
                  (None, None)])

def iterable_positions_test():
    def it():
        for c in "xy\nXY":
            yield c

    assert_equal(list(tokenize.positions(it())),
                 [('x', tokenize.Position(None, 1, 1)),
                  ('y', tokenize.Position(None, 1, 2)),
                  ('\n', tokenize.Position(None, 1, 3)),
                  ('X', tokenize.Position(None, 2, 1)),
                  ('Y', tokenize.Position(None, 2, 2)),
                  (None, None)])
