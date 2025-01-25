import lexkind
from core import Position, Range, Lexeme, Error

def _is_ident_begin(s):
    return _is_letter(s) or _is_special(s)

def _is_ident_continue(s):
    return _is_ident_begin(s) or _is_digit(s)

def _is_letter(s):
    return (s >= "a" and s <= "z") or (s >= "A" and s <= "Z")

def _is_special(s):
    return s in [
            "<", ">", "?", "=", "!",
            "-", "+", "*", "/", "%",
            "$", "_"
        ]

def _is_num_begin(s):
    return _is_digit(s) or s == "~"

def _is_digit(s):
    return s >= "0" and s <= "9"

def _is_digit_(s):
    return _is_digit(s) or s == "_"

def _is_hex_digit(s):
    return _is_digit(s) or (s >= "a" and s <= "f") or (s >= "A" and s <= "F") or s == "_"

def _is_bin_digit(s):
    return s in ["0", "1", "_"]

def lex(modname, string):
    return Lexer(modname, string).all_tokens()

class Lexer:
    def __init__(self, modname, string):
        self.string = string
        self.start = 0
        self.end = 0
        self.range = Range(Position(0, 0), Position(0, 0))
        self.word = None
        self.peeked = None
        self.modname = modname

    def next(self):
        if self.peeked != None:
            self.word = self.peeked
            self.peeked = None
        else:
            self.word = self._any()
        self._advance()
        return self.word

    def peek(self):
        if self.peeked == None:
            self.peeked = self._any()
        return self.peeked

    def all_tokens(self):
        all = []
        l = self.next()
        while not (l.kind in [lexkind.EOF, lexkind.INVALID]):
            all += [l]
            l = self.next()
        return all

    def _selected(self):
        return self.string[self.start:self.end]

    def _peek_rune(self):
        if self.end >= len(self.string):
            return ""
        return self.string[self.end]

    def _next_rune(self):
        if self.end >= len(self.string):
            return ""
        r = self.string[self.end]
        self.end += 1

        self.range.end.column += 1
        if r == "\n":
            self.range.end.line += 1
            self.range.end.column = 0
        
        return r

    def _emit(self, kind):
        s = self.string[self.start:self.end]
        return Lexeme(s, kind, self.range.copy())
    def _emit_str(self):
        s = self.string[self.start+1:self.end-1]
        s = _process_str(s)
        return Lexeme(s, lexkind.STR, self.range.copy())

    def _advance(self):
        self.start = self.end
        self.range.start = self.range.end.copy()

    def _ignore_whitespace(self):
        r = self._peek_rune()
        loop = True
        while loop:
            if r in [" ", "\r"]:
                self._next_rune()
            elif r == "#": # comment
                self._next_rune()
                r = self._peek_rune()
                while r != "\n" and r != "":
                    self._next_rune()
                    r = self._peek_rune()
            else:
                loop = False
            r = self._peek_rune()

        self._advance()

    def _any(self):
        self._ignore_whitespace()
        r = self._peek_rune()
        if _is_num_begin(r):
            return self._number()
        elif _is_ident_begin(r):
            return self._identifier()
        elif r == "'":
            return self._str()
        elif r == "[":
            self._next_rune()
            return self._emit(lexkind.LEFT_DELIM)
        elif r == "]":
            self._next_rune()
            return self._emit(lexkind.RIGHT_DELIM)
        elif r == ".":
            self._next_rune()
            return self._emit(lexkind.DOT)
        elif r == "\n":
            self._next_rune()
            return self._emit(lexkind.NL)
        elif r == "":
            return Lexeme("", lexkind.EOF, self.range.copy())
        else:
            self._next_rune()
            return Lexeme(r, lexkind.INVALID, self.range.copy())

    def _number(self):
        r = self._peek_rune()
        if not _is_num_begin(r):
            return None
        if r == "0":
            self._next_rune()
            r = self._peek_rune()
            if r == "x":
                self._next_rune()
                return self._num_hex()
            elif r == "b":
                self._next_rune()
                return self._num_bin()
        return self._num_decimal()

    def _num_decimal(self):
        r = self._peek_rune()
        if r == "~":
            self._next_rune()
        self._integer()
        r = self._peek_rune()
        if r in ['.', '/']:
            self._next_rune()
            self._integer()
            r = self._peek_rune()
        if r == 'e':
            self._next_rune()
            r = self._peek_rune()
            if r == "~":
                self._next_rune()
            self._integer()
        return self._emit(lexkind.NUM)

    def _num_hex(self):
        while _is_hex_digit(r):
            self._next_rune()
            r = self._peek_rune()
        return self._emit(lexkind.NUM)

    def _num_bin(self):
        while _is_bin_digit(r):
            self._next_rune()
            r = self._peek_rune()
        return self._emit(lexkind.NUM)

    def _integer(self):
        r = self._peek_rune()
        if _is_digit(r):
            self._next_rune()
            r = self._peek_rune()

            while _is_digit_(r):
                self._next_rune()
                r = self._peek_rune()

    def _identifier(self):
        r = self._peek_rune()
        while _is_ident_continue(r):
            self._next_rune()
            r = self._peek_rune()
        return self._emit(lexkind.ID)

    def _str(self):
        r = self._peek_rune()
        if r == "\'":
            self._next_rune()
            r = self._peek_rune()
        ok = True

        while ok:
            if r in ["", "\n"]:
                return self._emit(lexkind.INVALID)

            if r == "\\":
                self._next_rune()
                r = self._peek_rune()
                if not (r in ["n", "\'", "\\"]):
                    return self._emit(lexkind.INVALID)
            elif r == "\'":
                ok = False

            self._next_rune()
            r = self._peek_rune()
        # remove delimitadores
        return self._emit_str()

def _process_str(s):
    out = ""
    i = 0
    while i < len(s):
        r = s[i]
        if r == "\\":
            i += 1
            r = s[i]
            if r == "n":
                out += "\n"
            elif r == "'":
                out += "'"
            elif r == "\\":
                out += "\\"
        else:
            out += r
        i += 1
    return out
