import string
import collections

identifier_start = set(string.ascii_letters + '_')
identifier_inside = set(string.ascii_letters + '_' + string.digits)
simple_escapes = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
symbols = {'{', '}', '[', ']', ',', ':'}
digits = set(string.digits)
hexdigits = set(string.hexdigits)
whitespace = set(string.whitespace)
number_bases = {'x': 16, 'X': 16, 'o': 8, 'O': 8, 'b': 2, 'B': 2}

class Position(collections.namedtuple("Position", ["file", "line", "column"])):
    __slots__ = ()
    def __str__(self):
        if self.file is not None:
            return "{}, line {}, column {}".format(self.file, self.line, self.column)
        else:
            return "line {}, column {}".format(self.line, self.column)

def positions(data, filename = None):
    line = 1
    column = 0

    for char in data:
        column += 1
        yield (char, Position(filename, line, column))
        if char == '\n':
            line += 1
            column = 0

    yield None, None

def positions_file(fp, filename = None):
    line = 1
    column = 0

    if filename is None:
        try:
            filename = fp.name
        except AttributeError:
            pass

    while True:
        char = fp.read(1)
        if len(char) == 0:
            break

        column += 1
        yield (char, Position(filename, line, column))
        if char == '\n':
            line += 1
            column = 0

    yield None, None

def tokenize_iterable(string, filename = None):
    return tokenize(positions(string, filename))

def tokenize_file(fp, filename = None):
    return tokenize(positions_file(fp, filename))

def tokenize(it):
    for char, position in it:
        while char is not None:
            if char in symbols:
                yield (char, position)
                char = None
            elif char in ['/', '#']:
                skip_comment(char, position, it)
                char = None
            elif char == '"':
                yield "string", position, parse_string(char, position, it)
                char = None
            elif char in identifier_start:
                prev_position = position
                identifier, char, position = parse_identifier(char, position, it)
                if identifier == "true":
                    yield (True, prev_position)
                elif identifier == "false":
                    yield (False, prev_position)
                elif identifier == "null":
                    yield (None, prev_position)
                else:
                    yield "identifier", prev_position, identifier
            elif char in digits or char == '-':
                prev_position = position
                number_type, value, char, position = parse_number(char, position, it)
                yield number_type, prev_position, value
            elif char in whitespace:
                char = None
            else:
                raise ValueError("Unexpected character at " + str(position))

def skip_comment(char, position, iterator):
    assert char == '#' or char == '/'
    start_position = position

    if char == '#':
        skip_until_newline(iterator)
        return
    else:
        char, position = next(iterator)

        if char == '/':
            skip_until_newline(iterator)
            return
        elif char == '*':
            skip_block_comment(char, start_position, iterator)
            return

    raise ValueError("Invalid comment start encountered at " + str(start_position))

def skip_block_comment(char, position, iterator):
    assert char == '*'
    start_position = position

    had_star = False
    for char, position in iterator:
        if char == '*':
            had_star = True
        elif char == '/' and had_star:
            return
        else:
            had_star = False

    raise ValueError("Unterminated block comment at " + str(start_position))

def skip_until_newline(iterator):
    for char, position in iterator:
        if char == '\n':
            return

def parse_string(char, position, iterator):
    assert char == '"'
    start_position = position

    chars = []
    for char, position in iterator:
        if char == '"':
            return ''.join(chars)
        elif char == '\\':
            chars.append(parse_string_escape(char, position, iterator))
        elif char == '\n':
            raise ValueError("Unexpected newline in string at " + str(start_position))
        else:
            chars.append(char)

    raise ValueError("Unterminated string at " + str(start_position))

def parse_string_escape(char, position, iterator):
    """ Read a string escape sequence from the input and return the character it represents """
    assert char == '\\'
    start_position = position

    char, position = next(iterator)
    if char in simple_escapes:
        return simple_escapes[char]
    elif char == 'u':
        number = 0
        for i in range(4):
            char, position = next(iterator)
            if char not in hexdigits:
                number = None
                break
            else:
                number = number * 16 + int(char, 16)

        if number is not None:
            return chr(number)

    raise ValueError("Invalid string escape sequence at " + str(start_position))

def parse_identifier(char, position, iterator):
    assert char in identifier_start
    chars = [char]
    start_position = position

    for char, position in iterator:
        if char in identifier_inside:
            chars.append(char)
        else:
            return ''.join(chars), char, position

    return ''.join(chars), None, None

def parse_number(char, position, iterator):
    start_position = position
    negative = False

    if char == '-':
        negative = True
        char, position = next(iterator)

    if char == '0':
        char, position = next(iterator)

        if char in number_bases:
            return parse_number_base(start_position, number_bases[char], negative, iterator)
        elif char == '.':
            return parse_number_decimal(char, position, start_position, negative, iterator)
        elif char in digits: # Disallow numbers starting with zero
            char = None
        else:
            return ("number", 0, char, position)
    elif char in digits:
        return parse_number_decimal(char, position, start_position, negative, iterator)

    raise ValueError("Invalid number at " + str(start_position))

def parse_number_base(start_position, base, negative, iterator):
    char, position = next(iterator)

    try:
        value = int(char, base)
    except (ValueError, TypeError):
        raise ValueError("Invalid number -- need at least one digit at " + str(start_position))

    for char, position in iterator:
        try:
            value = value * base + int(char, base)
        except (ValueError, TypeError):
            break

    if negative:
        value = -value
    return ("ext_number", value, char, position)

def parse_number_decimal(char, position, start_position, negative, iterator):
    if char in digits:
        value = int(char)
        char = None

        for char, position in iterator:
            if char is None:
                break
            try:
                value = value * 10 + int(char)
            except ValueError:
                break
    else:
        assert char == '.'
        value = 0

    if char == '.':
        fractional, char, position = parse_number_fractional(char, start_position, iterator)
        value += fractional

    if char == 'e' or char == 'E':
        multiplier, char, position = parse_number_exponent(char, start_position, iterator)
        value *= multiplier

    if negative:
        value = -value
    return ("number", value, char, position)

def parse_number_fractional(char, start_position, iterator):
    assert char == '.'

    char, position = next(iterator)

    if char not in digits:
        raise ValueError("Invalid number -- missing number after decimal dot at " + str(start_position))

    multiplier = 0.1

    value = multiplier * int(char)

    for char, position in iterator:
        multiplier /= 10
        try:
            value += multiplier * int(char)
        except (ValueError, TypeError):
            break

    return (value, char, position)

def parse_number_exponent(char, start_position, iterator):
    assert char == 'e' or char == 'E'

    char, position = next(iterator)

    negative = False
    if char == '+' or char == '-':
        if char == '-':
            negative = True
        char, position = next(iterator)

    if char not in digits:
        raise ValueError("Invalid number -- missing exponent at " + str(start_position))

    if char in digits:
        number = int(char)
        char = None
    else:
        number = 0

    for char, position in iterator:
        try:
            number = number * 10 + int(char)
        except (ValueError, TypeError):
            break

    print(number)

    if negative:
        number = -number

    return (10**number, char, position)
