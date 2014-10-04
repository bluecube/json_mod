import json_mod.tokenize
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
    data = 'abcd { , [\ntrue "xyz"\n\n\n7 /* this is a comment\n! */ a'
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable(data),
                           [('identifier', json_mod.tokenize.Position(None, 1, 1), 'abcd'),
                            ('{', json_mod.tokenize.Position(None, 1, 6)),
                            (',', json_mod.tokenize.Position(None, 1, 8)),
                            ('[', json_mod.tokenize.Position(None, 1, 10)),
                            (True, json_mod.tokenize.Position(None, 2, 1)),
                            ('string', json_mod.tokenize.Position(None, 2, 6), 'xyz'),
                            ('number', json_mod.tokenize.Position(None, 5, 4), 7),
                            ('identifier', json_mod.tokenize.Position(None, 6, 6), 'a'),
                           ])

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

def json_number_test():
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1.2'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1.2)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('1.25'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 1.25)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42.5'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42.5)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('42.52'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 42.52)])
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

def ext_number_test():
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0x10'),
                           [('ext_number', json_mod.tokenize.Position(None, 1, 1), 16)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0b01001'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 9)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('0o21'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 17)])
    assert_iterables_equal(json_mod.tokenize.tokenize_iterable('021'),
                           [('number', json_mod.tokenize.Position(None, 1, 1), 17)])
