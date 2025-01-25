import lexkind
import nodekind

# esse arquivo contem as principais estruturas de dados
# e suas funcoes utilitarias

class Result:
    def __init__(self, value, error):
        #if type(value) is Result:
        #    raise
        self.value = value
        self.error = error

    def ok(self):
        return self.error == None

    def failed(self):
        return self.error != None

# representa uma posicao no codigo fonte
class Position:
    def __init__(self, line, column):
        self.line = line
        self.column = column
    def copy(self):
        return Position(self.line, self.column)
    def __str__(self):
        return str(self.line) + ":" + str(self.column)
    def correct_editor_view(self):
        # no lexer a gente comeca na linha 0, coluna 0,
        # mas no editor, nos vemos tudo comecando da
        # linha 1, coluna 1
        self.line += 1
        self.column += 1
    def less(self, other):
        if self.line < other.line:
            return True
        if self.line > other.line:
            return False
        # aqui as linhas sao iguais
        if self.column < other.column:
            return True
        return False
    def more(self, other):
        if self.line > other.line:
            return True
        if self.line < other.line:
            return False
        # aqui as linhas sao iguais
        if self.column > other.column:
            return True
        return False

# representa uma secao continua do codigo fonte
# start e end tem que ser da classe Position
class Range:
    def __init__(self, pos_start, pos_end):
        self.start = pos_start
        self.end = pos_end
    def copy(self):
        return Range(self.start.copy(),
                     self.end.copy())
    def __str__(self):
        out = self.start.__str__()
        out += " to "
        out += self.end.__str__()
        return out
    def correct_editor_view(self):
        self.start.correct_editor_view()
        self.end.correct_editor_view()

class Error:
    def __init__(self, module, string, range):
        self.module = module
        self.message = string
        self.range = range
    def __str__(self):
        if self.range != None:
            out = "error " + self.module
            out += ":"+ self.range.__str__()
            out += ": "+ self.message
            return out
        else:
            out = "error "+ self.module +": "
            out += self.message
            return out
    def copy(self):
        if self.range != None:
            return Error(self.module,
                         self.message,
                         self.range.copy())
        else:
            return Error(self.module,
                         self.message,
                         None)
    def correct_editor_view(self):
        if self.range != None:
            self.range.correct_editor_view()

class Lexeme:
    def __init__(self, string, kind, range):
        self.text = string
        self.kind = kind
        self.range = range
    def __str__(self):
        out = "('" + self.text + "', "
        out += lexkind.to_string(self.kind) + ")"
        return out
    def start_column(self):
        return self.range.start.column
    def copy(self):
        return Lexeme(self.string,
                      self.kind,
                      self.range.copy())

# value precisa ser um Lexeme
class Node:
    def __init__(self, value, kind):
        self.value = value
        self.kind = kind
        self.leaves = []
        self.range = None

    def add_leaf(self, leaf):
        self.leaves += [leaf]

    def left(self):
        return self.leaves[0]
    def right(self):
        return self.leaves[1]

    def has_lexkind(self, kind):
        return self.value.kind == kind

    def has_lexkinds(self, kinds):
        return self.value.kind in kinds

    def start_column(self):
        return self.range.start.column

    def compute_range(self):
        if self.kind == nodekind.TERMINAL:
            self.range = self.value.range.copy()
            return None
        if self.range == None:
            self.range = Range(Position(0, 0),
                               Position(0, 0))
        i = 0
        while i < len(self.leaves):
            leaf = self.leaves[i]

            if leaf != None:
                leaf.compute_range()
                other_start = leaf.range.start
                self_start = self.range.start
                if other_start.less(self_start):
                    self.range.start = other_start.copy()
                self_end = leaf.range.end
                other_end = self.range.end
                if other_end.more(self_end):
                    self.range.end = other_end.copy()
            i += 1

    def __str__(self):
        self.compute_range()
        out = ""
        for leaf in self.leaves:
            out += _print_tree(leaf, 0)
        return out

    def copy(self):
        leaves = []
        i = 0
        while i < len(self.leaves):
            leaf = self.leaves[i]

            leaves += [leaf.copy()]
            i += 1
        n = Node(self.value.copy())
        n.leaves = leaves
        return n

def _print_tree(node, indent):
    if node == None:
        return "nil\n"

    if node.kind == nodekind.TERMINAL:
        return node.value.text

    if len(node.leaves) == 0:
        return "()"

    out = ""
    line = node.range.start.line
    i = 0
    broken = False
    while i < len(node.leaves):
        n = node.leaves[i]
        curr_line = n.range.start.line
        if line < curr_line:
            out += "\n" + _indent(indent)
            line = curr_line
            if not broken:
                indent += 1
            broken = True
        if i == 0:
            out += "("

        out += _print_tree(n, indent)
        if i < len(node.leaves)-1:
            out += " "
        i += 1
    out += ")"
    return out

def _indent(n):
    i = 0
    out = ""
    while i < n:
        out += "  "
        i += 1
    return out
