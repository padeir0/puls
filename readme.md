# PULS

This is my attempt at creating an universal language
syntax that is not hard to type, not hard to read and
that can work well with dot-autocompletion of editors.

The language primary goal is to describe an abstract
syntax tree, just like S-Expressions, but the result
should look natural.

This document draws inspiration from
[S-expressions](https://www-sop.inria.fr/indes/fp/Bigloo/doc/r5rs-10.html#Formal-syntax),
[T-expressions](https://srfi.schemers.org/srfi-110/srfi-110.html),
[I-expressions](https://srfi.schemers.org/srfi-49/srfi-49.html),
[O-expressions](http://breuleux.net/blog/oexprs.html),
[M-expressions](https://en.m.wikipedia.org/wiki/M-expression) and
[Wisp](https://srfi.schemers.org/srfi-119/srfi-119.html).

Notation here is [Wirth Syntax Notation](https://dl.acm.org/doi/10.1145/359863.359883)
with extensions from the article
[Indentation-Sensitive Parsing for Parsec](https://osa1.net/papers/indentation-sensitive-parsec.pdf)
and [PCRE](https://www.pcre.org/original/doc/html/pcresyntax.html).

This extensions are, briefly:
 - the _justification operator_ `:` that forces the production to be in the same indentation as the parent production;
 - the _indentation operator_ `>` that forces the production to be in an indentation _strictly greater than_ the parent production;
 - the indentation level of a production, which is defined to be the column position of the first token that is consumend (or produced) in that production;
 - the production `Whitespace` that indicates tokens that serve only as separators and are otherwise ignored;
 - the regular expressions, which are inside `//`.

```ebnf
Whitespace = '\r' | ' ' | Comment.
Comment = '#' {not_newline_char} '\n'.

Program = Block.
Block = {:I_Expr NL}.

I_Expr = Pair {Pair} [NL >Block].
Pair = Term {'.' Term}.
Term = Atom | S_Expr.
S_Expr = '[' {Pair} ']'.

NL = '\n' {'\n'}.
Atom = id | num | str.

str = /'[\u0000-\uFFFF]*'/.

id = ident_begin {ident_continue}.
ident_begin = /[a-zA-Z_<>\?=!\-\+\*\/\%\$\']/.
ident_continue = ident_begin | digit.

num = hex | bin | dec.
dec = [neg] integer [frac | float].
integer = digit {digit_}.
frac = '/' integer.
float = '.' integer.

hex = '0x' hexdigits.
hexdigits = /[0-9A-Fa-f_]+/.
bin = '0b' bindigits.
bindigits = /[01_]+/.

neg = '~'.
digit = /[0-9]/.
digit_ = digit | '_'.
```

See that `.` can be used to implement autocompletion.
For example: `module.symbol`.
It can also be chained, like
`module.struct.field` (which means `[[module struct] field]`).

Note also that `.`, `[`, `]`, spaces and linebreaks
need no Shift nor Ctrl keys to type,
although identifiers may carry hard-to-type symbols, it is
completely optional to require them.
This means that, when we compare this with S-Expressions,
not only we polute our code less, we type *much* less
(specially if you use autocompletion).

One caveat: this design forbids using
line-breaks inside `[]`, this is intentional
since allowing it would create a mess,
the syntax would be too flexible.

## The Tree

This language simply defines an abstract syntax tree,
here, we will use S-Expressions to show how this tree
is parsed.

Consider the S-Expression `(f (a b) c d)`,
the following PULS expressions are equivalent:

```
[f [a b] c d]

f [a b] c d

f [a b] c
  d

f [a b]
  c
  d

f
  [a b]
  c
  d

f
  a b
  c
  d

f a.b c d

f a.b
  c
  d
```

Now, consider `(((a b) c) d)`,
in PULS, all of the following are equivalent.

```
[[[a b] c] d]

[[a b] c] d

a.b.c.d
```

Furthermore, if we consider `((a b) (c d) (e f))`,
in PULS, we have:

```
[[a b] [c d] [e f]]

[a.b c.d e.f]

a.b c.d e.f
```

We can also go further and write `(((a b) (c d)) ((e f) (g h)))`
as:

```
[[[a b] [c d]] [[e f] [g h]]]
[[a b] [c d]] [[e f] [g h]]
[a b].[c d] [e f].[g h]
```

## Examples

### Lisp-like languages

Here's a factorial procedure
written in Scheme.

```scheme
(define (fact n)
  (if (<= n 0)
    1
    (* n (fact (- n 1)))))
```

We can represent the same tree with:

```
define [fact n]
  if [<= n 0]
    1
    * n [fact [- n 1]]
```

### Assembly-like languages

We can readily accomodate the tabular
aspects of assembly-like languages.
Consider the following example, that
computes the first seven fibonacci numbers
in amd64:

```PULS
format [ELF64 executable 3]

segment [readable executable]
  entry
    mov rax 0
    mov rdx 1
    mov rcx 7
  _loop
    xadd rax rdx
    loop _loop
  _end
    mov rdi rax
    mov rax 60
    syscall
```

### Configuration files

The following is an example TOML
config file from my editor:

```toml
[editor.statusline]
mode.normal = "NORMAL"
mode.insert = "INSERT"
mode.select = "SELECT"
```

In PULS, this is can be simply represented:

```PULS
editor.statusline
  mode.normal 'NORMAL'
  mode.insert 'INSERT'
  mode.select 'SELECT'
```

The following is an excerpt from my i3 config file:

```
bindsym XF86MonBrightnessUp exec --no-startup-id brightnessctl set +1%
bindsym XF86MonBrightnessDown exec --no-startup-id brightnessctl set 1%-

bindsym Print exec gnome-screenshot -i -a

bar {
        status_command i3status
}
```

We can represent this in PULS
using strings to encapsulate Bash commands:

```PULS
bindsym XF86MonBrightnessUp
  exec --no-startup-id 'brightnessctl set +1%'
bindsym XF86MonBrightnessDown
  exec --no-startup-id 'brightnessctl set 1%-'

bindsym Print
  exec 'gnome-screenshot -i -a'

bar
  status_command i3status
```

Last, but not least, consider the following JSON:

```json
{
  "name": {
    "age": 25,
    "tokens": [32, 35, 75],
    "alive": true
  }
}
```

This can be represented in a million ways, but
here is one of them:

```PULS
'name'
  age.25
  tokens.[32 35 75]
  alive.true
```

To be a more honest with JSON,
you should probably represent it as:

```PULS
map
  "name"
    map
      age.25
      tokens.[array 32 35 75]
      alive.true
```

Which is not much better, but not much worse either.

### SQL-like languages

Consider the following select statement:

```SQL
SELECT name, birthday, country
FROM users
WHERE id = 314159
```

This fits very well in PULS:

```PULS
select 
  name birthday country
  from users
  where [= id 314159]
```

We can omit the `from` and `where` keywords, but they serve
as hints to the syntax tree structure.

### Shells

Most shell commands are directly
translatable to PULS. Consider the Bash
command:

```bash
grep -Pho '[a-zA-Z_][a-zA-Z0-9_\-\?\+\*\/]*' ./*.rkt | sort | uniq | column
```

(which i used once to pick all racket atoms i've used in a codebase)

This can be translated to:

```bash
pipe [grep 'Pho' '[a-zA-Z_][a-zA-Z0-9_\-\?\+\*\/]*' './*.rkt'] sort uniq column
```

Which is, arquably, much worse, but not impossible to get used to,
specially in the simpler cases, where you'd do:

```
find here name.'*.rkt'
```

Where `here` would represent the current directory `.`.

### Pascal-like languages

PULS permits us to write type declarations
without clutter:

```
type A [union T_1 ... T_n]

type B
  struct field_1.T_1
         ...
         field_n.T_n
```

And to place type annotations in procedures:

```
proc max [a.num b.num] num
     if [>= a b] a b
```

This allows us to write Pascal-like languages with
static types.

### Other data structures

We may represent matrices:

```
define Id
  matrix
    1 0 0
    0 1 0
    0 0 1
```

And dictionaries:

```
define M
  map 'one'.1 'two'.2 'three'.3
```

And graphs:

```
graph
  a b c       # vertices
  a.b a.c b.c # edges
```

And graphs again, by adjacency lists:

```
graph
  a b c
  b c
  c
```

And tables:

```
table
  month expenses revenue
  1     0        0
  2     100      100
  3     2        20
  4     0        +inf
```
