INVALID = -1

NUM = 0
STR = 1
ID = 2

LEFT_DELIM = 3
RIGHT_DELIM = 4

DOT = 5

NL = 6
EOF = 7

def to_string(kind):
    if kind == INVALID:
        return "INVALID"

    elif kind == NUM:
        return "NUM"
    elif kind == STR:
        return "STR"
    elif kind == ID:
        return "ID"

    elif kind == LEFT_DELIM:
        return "LEFT_DELIM"
    elif kind == RIGHT_DELIM:
        return "RIGHT_DELIM"

    elif kind == DOT:
        return "DOT"

    elif kind == NL:
        return "NL"
    elif kind == EOF:
        return "EOF"
    return "??"
