# PULS

This is my attempt at creating an universal programming language
syntax that is not hard to type, not hard to read and
that can work well with dot-autocompletion of editors.

```ebnf
Whitespace = '\r' | ' ' | Comment.
Comment = '#' {not_newline_char} '\n'.

Program = Block.
Block = {:Multiline_Expr NL}.

Multiline_Expr = Term IP_Expr.
Simple_Expr = Term {Pair_Expression}.
Term = Atom | S_Expr.

S_Expr = '[' {Simple_Expr} ']'.
IP_Expr = I_Expression | {Pair_Expression}.
Pair_Expression = '.' Term.

I_Expression = {Simple_Expr} [NL >Block].

NL = '\n' {'\n'}.
Atom = id | num | str.

str = /"[\u0000-\uFFFF]"/.

id = ident_begin {ident_continue}.
ident_begin = /[a-zA-Z_<>\?=!\+\*\/\%\$]/.
ident_continue = ident_begin | digit.

num = hex | bin | dec.
dec = [neg] integer [frac | float].
integer = digit {digit_}.
frac = '/' integer.
float = '.' integer.

neg = '~'.
digit = /[0-9]/.
digit_ = digit | '_'.
```

See that `.` can be used to implement autocompletion.
For example: `module.symbol`.
It can also be chained, like
`module.struct.field` (which means `[[module struct] field]`).

## Examples

Factorial can be written in S-Expressions in this way:

```scheme
(define (fact n)
  (if (<= n 0)
    1
    (* n (fact (- n 1)))))
```

In this syntax, we can rewrite it as:

```
define [fact n]
  if [<= n 0]
    1
    * n [fact [- n 1]]
```

We can go further, and write other things,
like matrices:

```
define Id
  matrix
    1 0 0
    0 1 0
    0 0 1
```

Instead of the S-Expression equivalent:

```scheme
(define A
  (matrix
    (1 0 0)
    (0 1 0)
    (0 0 1)))
```

And dictionaries:

```
define M
  map "one".1 "two".2 "three".3
```

Which, in S-Expressions, would be the same as:

```scheme
(define M
  (map ("one" 1)
       ("two" 2)
       ("three" 3)))
```

It permits us to write type declarations
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

