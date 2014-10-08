def parse(token_stream, enable_extensions = True):
    try:
        token = next(token_stream)

        if token[0] == '{':
            ret = parse_object(token, token_stream, enable_extensions)
        elif token[0] == '[':
            ret = parse_list(token, token_stream, enable_extensions)
        else:
            raise ValueError("Json payload must be an object or array at " + str(token[1]))
    except StopIteration:
        raise ValueError("Unexpected EOF")

    try:
        next(token_stream)
    except StopIteration:
        return ret
    except ValueError:
        pass

    raise ValueError("Trailing data")

    #TODO: Comments shoud raise the extensions exception!

def syntax_extension(token, enable_extensions):
    if not enable_extensions:
        raise ValueError("Extended syntax is disabled at " + str(token[1]))

def parse_value(token, token_stream, enable_extensions):
    if token[0] == "string" or token[0] == "number":
        return token[2]
    elif token[0] == True or token[0] == False or token[0] == None:
        return token[0]
    elif token[0] == "ext_number" or token[0] == "identifier":
        syntax_extension(token, enable_extensions)
        return token[2]
    elif token[0] == "{":
        return parse_object(token, token_stream, enable_extensions)
    elif token[0] == "[":
        return parse_list(token, token_stream, enable_extensions)
    else:
        raise ValueError("Invalid token encountered at " + str(token[1]))

def parse_object(token, token_stream, enable_extensions):
    assert token[0] == "{"

    ret = {}

    while True:
        token = next(token_stream)
        if token[0] == "string":
            key = token[2]
        elif token[0] == "identifier":
            syntax_extension(token, enable_extensions)
        elif token[0] == "}":
            if len(ret) != 0:
                syntax_extension(token, enable_extensions)
            return ret
        else:
            raise ValueError("Expected string as a key at " + str(token[1]))

        token = next(token_stream)
        if token[0] != ":":
            raise ValueError("Expected \":\" at " + str(token[1]))

        token = next(token_stream)
        ret[key] = parse_value(token, token_stream, enable_extensions)

        token = next(token_stream)
        if token[0] == ",":
            continue
        elif token[0] == "}":
            return ret;
        else:
            raise ValueError("Expected \",\" or \"}\" at " + str(token[1]))

def parse_list(token, token_stream, enable_extensions):
    assert token[0] == "["

    ret = []

    while True:
        token = next(token_stream)
        if token[0] == "]":
            if len(ret) != 0:
                syntax_extension(token, enable_extensions)
            return ret
        else:
            ret.append(parse_value(token, token_stream, enable_extensions))

        token = next(token_stream)
        if token[0] == ",":
            continue
        elif token[0] == "]":
            return ret;
        else:
            raise ValueError("Expected \",\" or \"]\" at " + str(token[1]))
