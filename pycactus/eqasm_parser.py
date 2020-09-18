# todo: when is the correct moment to convert immediate value into positive or negative?
# ------------------------------------------------------------
from pycactus.global_config import pycactus_root_dir
from pathlib import Path
import re
import ply.lex as lex
import ply.yacc as yacc
from pycactus.insn import *
from pycactus.utils import get_logger,  pycactus_msg
import logging

logger_lex = get_logger('lexer')
logger_lex.setLevel(logging.DEBUG)
logger_yacc = get_logger('yacc')
logger_yacc.setLevel(logging.DEBUG)


def debug_p(p):
    for i in range(1, len(p), 1):
        pycactus_debug('p[{}]: {}'.format(i, p[i]), end='  ')
    pycactus_debug('')


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
    'geu': 'COND_GEU'
}

tokens = [
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'COLON',
    # 'PLUS',
    # 'MINUS',
    # 'DIVIDE',
    # 'DOT',
    'HEX',
    'BINARY',
    'INTEGER',
    'IDENTIFIER',
    'RReg',
    'SREG',
    'TREG',
    'QREG',
    'PARALLEL'
] + list(reserved.values())

# Regular expression rules for simple tokens
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COLON = r":"
t_PARALLEL = r'\|'
# t_PLUS = r'\+'
# t_MINUS = r'-'
# t_DOT = "\."


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


def t_RReg(t):
    r'r\d+'
    t.type = 'RReg'
    logger_lex.debug('lex: [RReg: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])
    return t  # if no return, this token is thrown away


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
    logger_lex.debug('lex: [{}: {}]'.format(t.type, t.value))
    return t


def t_newline(t):
    r'\n+'
    logger_lex.debug(
        'lex: ************************* newline *************************')
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
# include the prefix ignore_ in the token declaration to force a token to be ignored
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'


# Error handling rule
def t_error(t):
    raise ValueError("Found illegal character '%s'" % t.value[0])
    # t.lexer.skip(1)


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


# lexer = lex.lex(debug=True, reflags=re.IGNORECASE)
lexer = lex.lex()


def p_root(p):
    '''root : insn_nop
            | insn_stop
            | insn_qwait
            | insn_qwaitr
            | insn_not
            | insn_cmp
            | insn_fmr
            | insn_ldi
            | insn_ldui
            | insn_ld
            | insn_st
            | insn_br
            | insn_fbr
            | insn_bundle
            | insn_rrr
            | insn_smis
            | insn_smit
    '''
    debug_p(p)
    p[0] = p[1]


def p_insn_nop(p):  # nop
    'insn_nop : NOP'

    debug_p(p)
    p[0] = Instruction(InsnName.NOP)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_stop(p):  # stop
    'insn_stop : STOP'

    debug_p(p)
    p[0] = Instruction(InsnName.STOP)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_qwait(p):  # qwait u_imm
    'insn_qwait : QWAIT imm'
    debug_p(p)
    p[0] = Instruction(InsnName.QWAIT, imm=p[2])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_qwaitr(p):  # qwaitr rs
    'insn_qwaitr : QWAITR r_reg'
    debug_p(p)
    p[0] = Instruction(InsnName.QWAITR, rs=p[2])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_not(p):  # not rd, rt
    'insn_not : NOT r_reg COMMA r_reg'
    debug_p(p)
    p[0] = Instruction(InsnName.NOT, rd=p[2], rt=p[4])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_cmp(p):
    'insn_cmp : CMP r_reg COMMA r_reg'
    debug_p(p)
    p[0] = Instruction(InsnName.CMP, rd=p[2], rt=p[4])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_fmr(p):  # fmr rd, qs
    'insn_fmr : FMR r_reg COMMA q_reg'

    debug_p(p)
    p[0] = Instruction(InsnName.FMR, rd=p[2], qs=p[4])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ldi(p):  # ldi rd, imm
    'insn_ldi : LDI r_reg COMMA imm'

    debug_p(p)
    p[0] = Instruction(InsnName.LDI, rd=p[2], imm=p[4])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ldui(p):  # ldui rd, u_imm
    'insn_ldui : LDUI r_reg COMMA imm'

    debug_p(p)
    p[0] = Instruction(InsnName.LDUI, rd=p[2], imm=p[4])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ld(p):  # lw/lb/lbu rd, rt(imm10)
    '''insn_ld : LW r_reg COMMA r_reg LPAREN imm RPAREN
               | LB r_reg COMMA r_reg LPAREN imm RPAREN
               | LBU r_reg COMMA r_reg LPAREN imm RPAREN
    '''

    debug_p(p)
    if (p[1]).lower() == 'lw':
        p[0] = Instruction(InsnName.LW, rd=p[2], rt=p[4], imm=p[6])
    elif (p[1]).lower() == 'lb':
        p[0] = Instruction(InsnName.LB, rd=p[2], rt=p[4], imm=p[6])
    elif (p[1]).lower() == 'lbu':
        p[0] = Instruction(InsnName.LBU, rd=p[2], rt=p[4], imm=p[6])

    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_st(p):  # sw/sb rs, rt(imm10)
    '''insn_st : SW r_reg COMMA r_reg LPAREN imm RPAREN
               | SB r_reg COMMA r_reg LPAREN imm RPAREN
    '''

    debug_p(p)
    if (p[1]).lower() == 'sw':
        p[0] = Instruction(InsnName.SW, rs=p[2], rt=p[4], imm=p[6])
    elif (p[1]).lower() == 'sb':
        p[0] = Instruction(InsnName.SB, rs=p[2], rt=p[4], imm=p[6])
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_br(p):
    'insn_br : BR cond COMMA offset_to_label'
    p[0] = 0


def p_insn_fbr(p):
    'insn_fbr : FBR cond COMMA r_reg'
    p[0] = 0


def p_insn_bundle(p):
    'insn_bundle : '


def p_insn_rrr(p):  # add/sub/or/xor/and  rd, rs, rt
    '''insn_rrr : ADD RReg COMMA RReg COMMA RReg
                | SUB RReg COMMA RReg COMMA RReg
                | OR RReg COMMA RReg COMMA RReg
                | XOR RReg COMMA RReg COMMA RReg
                | AND RReg COMMA RReg COMMA RReg
    '''
    debug_p(p)
    if p[1] == 'add':
        insn = Instruction(InsnName.ADD, rd=p[2], rs=p[4], rt=p[6])
    elif p[1] == 'sub':
        insn = Instruction(InsnName.SUB, rd=p[2], rs=p[4], rt=p[6])
    elif p[1] == 'or':
        insn = Instruction(InsnName.OR, rd=p[2], rs=p[4], rt=p[6])
    elif p[1] == 'xor':
        insn = Instruction(InsnName.XOR, rd=p[2], rs=p[4], rt=p[6])
    elif p[1] == 'and':
        insn = Instruction(InsnName.AND, rd=p[2], rs=p[4], rt=p[6])
    else:
        raise ValueError("Found mismatched pattern {}".format(p[1]))

    p[0] = insn

    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_smis(p):
    'insn_smis : SMIS s_reg COMMA s_mask'

    debug_p(p)
    insn = Instruction(InsnName.SMIS, si=p[2], sq_list=p[4])
    p[0] = insn
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_smit(p):
    'insn_smit : SMIT t_reg COMMA t_mask'

    debug_p(p)
    logger_yacc.info("processing smit...")
    insn = Instruction(InsnName.SMIT, ti=p[2], tq_list=p[4])
    p[0] = insn
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_r_reg(p):
    'r_reg : RReg'
    p[0] = p[1]


def p_q_reg(p):
    'q_reg : QREG'
    p[0] = p[1]


def p_s_reg(p):
    's_reg : SREG'
    p[0] = p[1]


def p_t_reg(p):
    't_reg : TREG'
    p[0] = p[1]


def p_single_qubit_list(p):
    '''single_qubit_list : INTEGER
                         | single_qubit_list COMMA INTEGER'''

    debug_p(p)
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        # p[0] = list(p[1]).append(p[3])
        p[1].append(p[3])
        p[0] = p[1]
    logger_yacc.debug("single_qubit_list: {}".format(p[0]))


def p_s_mask(p):
    's_mask : LBRACE single_qubit_list RBRACE'

    debug_p(p)
    p[0] = p[2]
    logger_yacc.info("s_mask: {}".format(p[0]))


def p_qubit_pair(p):
    '''qubit_pair : LPAREN INTEGER COMMA INTEGER RPAREN'''

    pycactus_debug('p_qubit_pair:', end='')
    debug_p(p)
    p[0] = (p[2], p[4])
    logger_yacc.debug("qubit_pair: {}".format(p[0]))


def p_two_qubit_list(p):
    '''two_qubit_list : qubit_pair
                      | two_qubit_list COMMA　qubit_pair
    '''
    pycactus_debug('p_two_qubit_list:', end='')
    debug_p(p)
    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
    logger_yacc.debug("two_qubit_list: {}".format(p[0]))


def p_t_mask(p):
    't_mask : LBRACE two_qubit_list RBRACE'
    debug_p(p)
    p[0] = p[2]
    logger_yacc.info("t_mask: {}".format(p[0]))


def p_imm(p):
    '''imm : INTEGER
    '''
    debug_p(p)
    p[0] = p[1]
    logger_yacc.info("imm: {}".format(p[0]))


def p_label_decl(p):
    'label_decl : IDENTIFIER COLON'

    debug_p(p)
    label = p[2]
    logger_yacc.info("found label: ", label)
    p[0] = label


def p_offset_to_label(p):
    'offset_to_label : IDENTIFIER'

    debug_p(p)
    label = p[1]
    p[0] = label
    logger_yacc.info("target label: {}".format(label))


def p_cond(p):
    '''cond : COND_ALWAYS
            | COND_NEVER
            | COND_EQ
            | COND_NE
            | COND_LT
            | COND_LE
            | COND_GT
            | COND_GE
            | COND_LTU
            | COND_LEU
            | COND_GTU
            | COND_GEU
    '''

    debug_p(p)
    p[0] = p[1]
    logger_yacc.info("condition: {}".format(p[0]))

# def p_error(p):
#     print("Syntax error in input!")


start = 'insn_smit'
parser = yacc.yacc(debug=True)

eqasm_dir = pycactus_root_dir / 'tests' / 'eqasm'
# custom_file = eqasm_dir / 'custom.eqasm'
custom_file = eqasm_dir / 'smit.eqasm'
data = custom_file.read_text()

# Give the lexer some input
# lexer.input(data.lower())

# for token in lexer:
#     print(token)

# print_format = "{:<15}  {:<15}  {:<15}  {:<15}"
# print(print_format.format("Type", "value", "lineno", "lexpos"))
# Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(print_format.format(tok.type, tok.value, tok.lineno, tok.lexpos))


result = parser.parse(data.lower())
print(result)
