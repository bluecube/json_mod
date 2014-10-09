from . import tokenize
from . import parse

def load(fp, filename = None, enable_extensions = True):
    characters = tokenize.positions_file(fp, filename)
    token_stream = tokenize.tokenize(characters, enable_extensions)
    return parse.parse(token_stream, enable_extensions)

def loads(iterable, filename = None, enable_extensions = True):
    characters = tokenize.positions(fp, filename)
    token_stream = tokenize.tokenize(characters, enable_extensions)
    return parse.parse(token_stream, enable_extensions)
