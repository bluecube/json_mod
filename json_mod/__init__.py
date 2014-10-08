from . import tokenize
from . import parse

def load(fp, filename = None, enable_extensions = True):
    token_stream = tokenize.tokenize_file(fp, filename = filename)
    return parse.parse(token_stream, enable_extensions)

def loads(iterable, filename = None, enable_extensions = True):
    token_stream = tokenize.tokenize_iterable(iterable, filename = filename)
    return parse.parse(token_stream, enable_extensions)
