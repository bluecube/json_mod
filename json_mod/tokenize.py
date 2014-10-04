import string
import collections

identifier_start = set(string.ascii_letters + '_')
identifier_inside = set(string.ascii_letters + '_' + string.digits)
simple_escapes = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
symbols = {'{', '}', '[', ']', ',', ':'}
digits = set(string.digits)
hexdigits = set(string.hexdigits)
whitespace = set(string.whitespace)

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
        if char == '\n':
            line += 1
            column = 0
        else:
            column += 1

        yield (char, Position(filename, line, column))

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

        if char == '\n':
            line += 1
            column = 0
        else:
            column += 1

        yield (char, Position(filename, line, column))

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
        try:
            char, position = next(iterator)
        except StopIteration:
            char = None

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

    try:
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

    except StopIteration:
        pass

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
    raise NotImplementedError("Numbers are not supported yet")
