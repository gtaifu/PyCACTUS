# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of token names.   This is always required

reserved = {
    'nop': 'NOP',
    'stop': 'STOP',
    'qwait': 'QWAIT',
    'qwaitr': 'QWAITR',
    'bundle': 'BUNDLE',
    'smis': 'SMIS',
    'smit': 'SMIT',
    'not': 'NOT',
    'cmp': 'CMP',
    'br': 'BR',
    'fbr': 'FBR',
    'fmr': 'FMR',
    'ldi': 'LDI',
    'add': 'ADD',
    'sub': 'SUB',
    'or': 'OR',
    'xor': 'XOR',
    'and': 'AND',
    'ldui': 'LDUI',
    'lw': 'LW',
    'lb': 'LB',
    'lbu': 'LBU',
    'sb': 'SB',
    'sw': 'SW'
}

tokens = [
    # 'LPAREN',
    # 'RPAREN',
    # 'LBRACE',
    # 'RBRACE',
    'COMMA',
    'COLON',
    'EQUAL',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'DOT',
    'NUMBER',
    'IDENTIFIER',
    'GPR',
    'PARALLEL',
    'RIGHT_ARROW'
] + list(reserved.values())

literals = ['{', '}', '(', ')', ',']
# Regular expression rules for simple tokens
# t_LPAREN = r'\('
# t_RPAREN = r'\)'
# t_LBRACE = r"\{"
# t_RBRACE = r"\}"
t_COMMA = r","
t_COLON = r":"
t_PARALLEL = r'\|'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DOT = "\."


# A regular expression rule with some action code

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_GPR(t):
    r'r\d+'
    t.type = 'GPR'
    t.value = int(t.value[1:])
    return t  # if no return, this token is thrown away


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
    return t

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
# include the prefix ignore_ in the token declaration to force a token to be ignored
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.'


# Error handling rule
def t_error(t):
    raise ValueError("Found illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# Build the lexer
lexer = lex.lex()


# Test it out
data = '''
ADDI r7, r0, 0
ARRAY_0:
CMP r7, r5
NOP
FBR LE, r8
BNE r8, r1, ARRAY_0_END
LDI r9, 0x1001c
LDUI r9, r9, 0x0
ADDI r9, r2, 0
ADDI r10, r0, 2 ///
SW r10, 0(r9)
ADDI r2, r2, 6
SW r9, 0(r6)

1, H s0
2, H s1
SMIT t0, {(0,1)}
2, CZ t0
2, H s1
function_5_end:

LDI r25, 0x1009e
LDUI r25, r25, 0x0
'''

# Give the lexer some input
lexer.input(data)

# for token in lexer:
#     print(token)

print_format = "{:<15}  {:<15}  {:<15}  {:<15}"
print(print_format.format("Type", "value", "lineno", "lexpos"))
# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break      # No more input

    print(print_format.format(tok.type, tok.value, tok.lineno, tok.lexpos))
