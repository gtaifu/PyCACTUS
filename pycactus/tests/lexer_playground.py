# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

import logging
from pycactus.utils import get_logger
logger_lex = get_logger('lexer')
logger_lex.setLevel(logging.INFO)

reserved = {
    'nop': 'NOP',
    'stop': 'STOP',
    'qwait': 'QWAIT',
    'qwaitr': 'QWAITR',
    'smis': 'SMIS',
    'smit': 'SMIT',
    'not': 'NOT',
    'cmp': 'CMP',
    'br': 'BR',
    'fbr': 'FBR',
    'fmr': 'FMR',
    'ldi': 'LDI',
    'add': 'ADD',
    'addi': 'ADDI',
    'sub': 'SUB',
    'or': 'OR',
    'xor': 'XOR',
    'and': 'AND',
    'ldui': 'LDUI',
    'lw': 'LW',
    'lb': 'LB',
    'lbu': 'LBU',
    'sb': 'SB',
    'sw': 'SW',
    'always': 'COND_ALWAYS',
    'never': 'COND_NEVER',
    'eq': 'COND_EQ',
    'ne': 'COND_NE',
    'lt': 'COND_LT',
    'le': 'COND_LE',
    'gt': 'COND_GT',
    'ge': 'COND_GE',
    'ltu': 'COND_LTU',
    'leu': 'COND_LEU',
    'gtu': 'COND_GTU',
    'geu': 'COND_GEU',
    'bra': 'BRA',
    'goto': 'GOTO',
    'brn': 'BRN',
    'beq': 'BEQ',
    'bne': 'BNE',
    'blt': 'BLT',
    'ble': 'BLE',
    'bgt': 'BGT',
    'bge': 'BGE',
    'bltu': 'BLTU',
    'bleu': 'BLEU',
    'bgtu': 'BGTU',
    'bgeu': 'BGEU',
    'fcvt.w.s': 'FCVT_W_S',
    'fcvt.s.w': 'FCVT_S_W',
    'flw': 'FLW',
    'fsw': 'FSW',
    'fadd.s': 'FADD_S',
    'fsub.s': 'FSUB_S',
    'fmul.s': 'FMUL_S',
    'fdiv.s': 'FDIV_S',
    'feq.s': 'FEQ_S',
    'flt.s': 'FLT_S',
    'fle.s': 'FLE_S',
    'qnop': 'QNOP',
    'bs': 'BS'
}

tokens = [
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'COLON',
    'NEWLINE',
    'HEX',
    'BINARY',
    'INTEGER',
    'IDENTIFIER',
    'RREG',
    'SREG',
    'TREG',
    'QREG',
    'VBAR'
] + list(reserved.values())

# Regular expression rules for simple tokens
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COLON = r":"
t_VBAR = r'\|'


def t_HEX(t):
    r'0x[0-9a-fA-F]+'
    t.type = 'INTEGER'
    logger_lex.debug('lex: [hex string: {}, value: {}]'.format(
        t.value, int(t.value, base=16)))
    t.value = int(t.value, base=16)
    return t


def t_BINARY(t):
    r'0b[01]+'
    t.type = 'INTEGER'
    logger_lex.debug('lex: [bin string: {}, value: {}]'.format(
        t.value, int(t.value, base=2)))
    t.value = int(t.value, base=2)
    return t


def t_INTEGER(t):
    r'[-]?\d+'
    t.value = int(t.value)
    logger_lex.debug('lex: [integer string: {}, value: {}]'.format(
        t.value, int(t.value)))

    return t


def t_COMMA(t):
    r","
    return t


def t_QReg(t):
    r'q\d+'
    t.type = 'QREG'
    logger_lex.debug('lex: [QReg: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])

    return t


def t_SReg(t):
    r's\d+'
    t.type = 'SREG'
    logger_lex.debug('lex: [SReg: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])
    return t


def t_TReg(t):
    r't\d+'
    t.type = 'TREG'
    logger_lex.debug('lex: [TReg: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])
    return t


def t_RREG(t):
    r'r\d+'
    t.type = 'RREG'
    logger_lex.debug('lex: [RREG: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])
    return t  # if no return, this token is thrown away


def t_IDENTIFIER(t):
    r'[a-zA-Z_][\.a-zA-Z_0-9]*'
    # Check for reserved words
    # print('found token: {}'.format(t.value))
    t.type = reserved.get(t.value, 'IDENTIFIER')
    # print('token type: {}'.format(t.type))
    logger_lex.debug('lex: [{}: {}]'.format(t.type, t.value))
    return t


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += len(t.value)
    return t

# def t_eof(t):
#     t.type = 'NEWLINE'
#     return t


t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test it out
data = '''
FCVT.S.W f0, r0
FCVT.W.S rd, rs1
'''

# Give the lexer some input
lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok.type, tok.value, tok.lineno, tok.lexpos)
