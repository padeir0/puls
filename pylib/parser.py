import lexkind
import nodekind
from lexer import Lexer
from core import Result, Node, Error, Range

def parse(modname, string, track):
    parser = _Parser(Lexer(modname, string))
    if track:
        parser.start_tracking()
    parser.track("parser.parse")

    _discard_nl(parser)
    res = _block(parser)
    if res.failed():
        return res

    if not parser.word_is(lexkind.EOF):
        err = parser.error("unexpected token or symbol")
        return Result(None, err)

    return res

class _Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.indent = 0 # numero de espacos
        self.is_tracking = False
        lexer.next() # precisamos popular lexer.word

    def error(self, str):
        return Error(self.lexer.modname, str, self.lexer.word.range.copy())

    def consume(self):
        if self.word_is(lexkind.INVALID):
            err = self.error("invalid character")
            return Result(None, err)
        out = self.lexer.word
        self.lexer.next()
        n = Node(out, nodekind.TERMINAL)
        return Result(n, None)

    def expect(self, kind, str):
        if self.word_is(kind):
            return self.consume()
        err = self.error("expected " + str)
        return Result(None, err)

    def expect_prod(self, production, text):
        res = production(self)
        if res.failed():
            return res
        if res.value == None:
            err = self.error("expected " + text)
            return Result(None, err)
        return res
        
    # implements:
    #     {Production}
    def repeat(self, production):
        list = []
        res = production(self)
        if res.failed() or res.value == None:
            return res

        last = res.value
        while last != None:
            list += [last]

            res = production(self)
            if res.failed():
                return res
            last = res.value
        return Result(list, None)

    def start_tracking(self):
        self.is_tracking = True

    def track(self, str):
        if self.is_tracking:
            print(str + ":" + self.lexer.word.__str__())

    def word_is_one_of(self, kinds):
        return self.lexer.word.kind in kinds

    def word_is(self, kind):
        return self.lexer.word.kind == kind

    def curr_indent(self):
        return self.lexer.word.start_column()

    def same_indent(self, base_indent):
        return self.curr_indent() == base_indent and not self.word_is(lexkind.EOF)

    def indent_prod(self, base_indent, production):
        prev_indent = self.indent
        self.indent = base_indent

        if not (self.curr_indent() > self.indent):
            return Result(None, None)

        res = production(self)
        if res.failed():
            return res
        out = res.value
        self.indent = prev_indent
        return Result(out, None)

# Block = {:I_Expr NL}.
def _block(parser):
    parser.track("_block")
    leaves = []

    base_indent = parser.curr_indent()
    while parser.same_indent(base_indent):
        res = _i_expr(parser)
        if res.failed():
            return res
        exp = res.value

        if parser.word_is(lexkind.NL):
            res = _NL(parser)
            if res.failed():
                return res

        if exp != None:
            leaves += [exp]

    if len(leaves) == 0:
        return Result(None, None)

    list = Node(None, nodekind.LIST)
    list.leaves = leaves
    return Result(list, None)

# I_Expr = Pair {Pair} [NL >Block].
def _i_expr(parser):
    parser.track("_i_expr")

    res = parser.repeat(_pair)
    if res.failed():
        return res
    leaves = res.value
    if len(leaves) == 0:
        return Result(None, None)

    if parser.word_is(lexkind.NL):
        res = _NL(parser)
        if res.failed():
            return res

        leaves[0].compute_range()
        start_column = leaves[0].start_column()
        res = parser.indent_prod(start_column, _block)
        if res.failed():
            return res
        block = res.value
        if block != None:
            leaves += block.leaves

    if len(leaves) == 1:
        return Result(leaves[0], None)

    list = Node(None, nodekind.LIST)
    list.leaves = leaves
    return Result(list, None)

# Pair = Term {'.' Term}.
def _pair(parser):
    parser.track("_pair")
    res = _term(parser)
    if res.failed() or res.value == None:
        return res
    first = res.value

    res = parser.repeat(_dot_term)
    if res.failed():
        return res
    if res.value != None:
        leaves = [first] + res.value
        root = leaves[0]
        i = 1
        while i < len(leaves):
            n = Node(None, nodekind.LIST)
            n.leaves = [root, leaves[i]]
            root = n
            i += 1
        return Result(root, None)
    return Result(first, None)

# '.' Term
def _dot_term(parser):
    parser.track("_dot_term")
    if parser.word_is(lexkind.DOT):
        res = parser.consume()
        if res.failed():
            return res
        res = parser.expect_prod(_term, "term")
        if res.failed():
            return res
        return res
    return Result(None, None)

# Term = Atom | S_Expr.
def _term(parser):
    parser.track("_term")
    if parser.word_is(lexkind.LEFT_DELIM):
        return _s_expr(parser)
    else:
        return _atom(parser)

# S_Expr = '[' {Pair} ']'.
def _s_expr(parser):
    parser.track("_s_expr")
    res = parser.expect(lexkind.LEFT_DELIM, "[")
    if res.failed():
        return res
    left_delim = res.value.value

    res = parser.repeat(_pair)
    if res.failed():
        return res
    leafs = res.value

    res = parser.expect(lexkind.RIGHT_DELIM, "]")
    if res.failed():
        return res
    right_delim = res.value.value

    list = Node(None, nodekind.LIST)
    list.leaves = leafs
    list.range = Range(left_delim.range.start,
                       right_delim.range.end)
    return Result(list, None)

# Atom = id | num | str.
def _atom(parser):
    parser.track("_atom")
    if parser.word_is_one_of([lexkind.ID,
                              lexkind.NUM,
                              lexkind.STR]):
        return parser.consume()
    elif parser.word_is(lexkind.INVALID):
        err = parser.error("invalid character")
        return Result(None, err)
    return Result(None, None)

# NL = nl {nl}.
def _NL(parser):
    parser.track("_NL")
    res = parser.expect(lexkind.NL, "line break")
    if res.failed():
        return res
    _discard_nl(parser)
    return Result(None, None)

def _discard_nl(parser):
    while parser.word_is(lexkind.NL):
        parser.consume()
