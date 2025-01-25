INVALID  = -1
TERMINAL = 0
LIST     = 1

def to_str(kind):
    if kind == INVALID: 
        return "INVALID"
    elif kind == TERMINAL: 
        return "TERMINAL"
    elif kind == LIST:
        return "LIST"
    else:
        return "???"
