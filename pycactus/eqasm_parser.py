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
logger_lex.setLevel(logging.INFO)
logger_yacc = get_logger('yacc')
logger_yacc.setLevel(logging.INFO)


def debug_p(p):
    for i in range(1, len(p), 1):
        pycactus_debug('p[{}]: {}'.format(i, p[i]), end='  ')
    pycactus_debug('')

# --------------------------- Lexer -----------------------------------


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
    # 'PLUS',
    # 'MINUS',
    # 'DIVIDE',
    # 'DOT',
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


def t_RREG(t):
    r'r\d+'
    t.type = 'RREG'
    logger_lex.debug('lex: [RREG: {}, value: {}]'.format(
        t.value, int(t.value[1:])))
    t.value = int(t.value[1:])
    return t  # if no return, this token is thrown away


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
    logger_lex.debug('lex: [{}: {}]'.format(t.type, t.value))
    return t


def t_NEWLINE(t):
    r'\n'
    logger_lex.debug(
        'lex: ************************* newline *************************')
    t.lexer.lineno += len(t.value)
    return t


# def t_eof(t):
#     t.type = 'NEWLINE'
#     return t


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


# --------------------------- Parser -----------------------------------

_instructions = []
_label_addr = {}


def p_root(p):
    '''root : program
    '''
    p[0] = p[1]


def p_program(p):
    '''program : instruction
               | program instruction
    '''
    if len(p) == 2:
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]
    else:
        if isinstance(p[2], list):
            p[1].extend(p[2])
        else:
            p[1].append(p[2])
        p[0] = p[1]
    logger_yacc.info("program, _label_addr: {}".format(_label_addr))

# TODO: add definition def_sym and .register


def p_instruction(p):
    '''instruction : NEWLINE
                   | label_decl           NEWLINE
                   | statement            NEWLINE
                   | label_decl statement NEWLINE
    '''
    p[0] = p[1]
    logger_yacc.info("instruction, _label_addr: {}".format(_label_addr))


def p_statement(p):
    '''statement : classic_statement
                 | quantum_statement
    '''
    p[0] = p[1]


def p_classic_statement(p):
    '''classic_statement : insn_nop
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
                         | insn_rrr
                         | insn_addi
                         | insn_smis
                         | insn_smit
                         | insn_bra
                         | insn_goto
                         | insn_brn
                         | insn_bcond
    '''
    p[0] = p[1]


def p_quantum_statement(p):
    '''quantum_statement : qbs quantum_instructions
                         | quantum_instructions
    '''
    if len(p) == 3:
        bs = p[1]
        q_ops = p[2]
    else:
        bs = 1
        q_ops = p[1]
    insn = Instruction(InsnName.BUNDLE, bs=bs, q_ops=q_ops)
    _instructions.append(insn)
    p[0] = insn


def p_qbs(p):
    '''qbs : optional_bs INTEGER COMMA
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = 1


def p_optional_bs(p):
    '''optional_bs :
                   | BS
    '''
    p[0] = None


def p_quantum_instructions(p):
    '''quantum_instructions : quantum_instruction
                            | quantum_instructions VBAR quantum_instruction
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
    logger_yacc.debug('quantum_instructions: {}'.format(p[0]))


def p_quantum_instruction(p):
    '''quantum_instruction : nq_op
                           | sq_op
                           | tq_op
    '''
    p[0] = p[1]
    logger_yacc.debug('p_quantum_instruction: {}'.format(p[0]))


def p_nq_op(p):
    'nq_op : QNOP'
    p[0] = Quantum_op('QNOP')
    logger_yacc.debug('nq_op: {}'.format(p[0]))


def p_sq_op(p):
    '''sq_op : IDENTIFIER s_reg
    '''
    p[0] = Quantum_op(p[1], sreg=p[2])
    logger_yacc.debug('sq_op: {}'.format(p[0]))


def p_tq_op(p):
    '''tq_op : IDENTIFIER t_reg
    '''
    p[0] = Quantum_op(p[1], treg=p[2])
    logger_yacc.debug('tq_op: {}'.format(p[0]))


def p_insn_nop(p):  # nop
    'insn_nop : NOP'

    p[0] = insn = Instruction(InsnName.NOP)
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_stop(p):  # stop
    'insn_stop : STOP'

    p[0] = insn = Instruction(InsnName.STOP)
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_qwait(p):  # qwait u_imm
    'insn_qwait : QWAIT imm'
    p[0] = insn = Instruction(InsnName.QWAIT, imm=p[2])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_qwaitr(p):  # qwaitr rs
    'insn_qwaitr : QWAITR r_reg'
    p[0] = insn = Instruction(InsnName.QWAITR, rs=p[2])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_not(p):  # not rd, rt
    'insn_not : NOT r_reg COMMA r_reg'
    p[0] = insn = Instruction(InsnName.NOT, rd=p[2], rt=p[4])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_cmp(p):
    'insn_cmp : CMP r_reg COMMA r_reg'
    p[0] = insn = Instruction(InsnName.CMP, rs=p[2], rt=p[4])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_fmr(p):  # fmr rd, qs
    'insn_fmr : FMR r_reg COMMA q_reg'

    p[0] = insn = Instruction(InsnName.FMR, rd=p[2], qs=p[4])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ldi(p):  # ldi rd, imm
    'insn_ldi : LDI r_reg COMMA imm'

    p[0] = insn = Instruction(InsnName.LDI, rd=p[2], imm=p[4])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ldui(p):  # ldui rd, rs, u_imm
    'insn_ldui : LDUI r_reg COMMA r_reg COMMA imm'

    p[0] = insn = Instruction(InsnName.LDUI, rd=p[2], rs=p[4], imm=p[6])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_ld(p):  # lw/lb/lbu rd, imm10(rt)
    '''insn_ld : LW r_reg COMMA r_reg LPAREN imm RPAREN
               | LB r_reg COMMA r_reg LPAREN imm RPAREN
               | LBU r_reg COMMA r_reg LPAREN imm RPAREN
    '''

    if (p[1]).lower() == 'lw':
        insn = Instruction(InsnName.LW, rd=p[2], imm=p[4], rt=p[6])
    elif (p[1]).lower() == 'lb':
        insn = Instruction(InsnName.LB, rd=p[2], imm=p[4], rt=p[6])
    elif (p[1]).lower() == 'lbu':
        insn = Instruction(InsnName.LBU, rd=p[2], imm=p[4], rt=p[6])
    else:
        assert(False)

    _instructions.append(insn)
    p[0] = insn
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_st(p):  # sw/sb rs, imm10(rt)
    '''insn_st : SW r_reg COMMA imm LPAREN r_reg RPAREN
               | SB r_reg COMMA imm LPAREN r_reg RPAREN
    '''

    if (p[1]).lower() == 'sw':
        insn = Instruction(InsnName.SW, rs=p[2], imm=p[4], rt=p[6])
    elif (p[1]).lower() == 'sb':
        insn = Instruction(InsnName.SB, rs=p[2], imm=p[4], rt=p[6])
    else:
        assert(False)
    p[0] = insn
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_br(p):
    'insn_br : BR cond COMMA offset_to_label'
    insn = Instruction(InsnName.BR, cmp_flag=p[2],
                       target_label=p[2])
    _instructions.append(insn)
    p[0] = insn


def p_insn_bra(p):
    '''insn_bra : BRA offset_to_label
    '''
    insn = Instruction(InsnName.BR, cmp_flag='ALWAYS',
                       target_label=p[2])
    _instructions.append(insn)
    p[0] = insn

    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_goto(p):
    '''insn_goto : GOTO offset_to_label
    '''
    p[0] = insn = Instruction(InsnName.BR, cmp_flag='ALWAYS',
                              target_label=p[2])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_brn(p):
    '''insn_brn : BRN offset_to_label
    '''
    p[0] = insn = Instruction(InsnName.BR, cmp_flag='NEVER',
                              target_label=p[2])
    _instructions.append(insn)
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_bcond(p):
    '''insn_bcond : BEQ r_reg COMMA r_reg COMMA offset_to_label
                  | BNE r_reg COMMA r_reg COMMA offset_to_label
                  | BLT r_reg COMMA r_reg COMMA offset_to_label
                  | BLE r_reg COMMA r_reg COMMA offset_to_label
                  | BGT r_reg COMMA r_reg COMMA offset_to_label
                  | BGE r_reg COMMA r_reg COMMA offset_to_label
                  | BLTU r_reg COMMA r_reg COMMA offset_to_label
                  | BLEU r_reg COMMA r_reg COMMA offset_to_label
                  | BGTU r_reg COMMA r_reg COMMA offset_to_label
                  | BGEU r_reg COMMA r_reg COMMA offset_to_label
    '''
    insn0 = Instruction(InsnName.CMP, rs=p[2], rt=p[4])
    insn1 = Instruction(InsnName.BR, CMP_FLAG=p[1][1:],
                        target_label=p[6])
    _instructions.append(insn0)
    _instructions.append(insn1)
    p[0] = [insn0, insn1]
    logger_yacc.info("Insn added: {}, {}".format(insn0, insn1))


def p_insn_fbr(p):
    'insn_fbr : FBR cond COMMA r_reg'
    insn = Instruction(InsnName.FBR, cmp_flag=p[2], rd=[4])
    _instructions.append(insn)
    p[0] = insn


def p_insn_rrr(p):  # add/sub/or/xor/and  rd, rs, rt
    '''insn_rrr : ADD r_reg COMMA r_reg COMMA r_reg
                | SUB r_reg COMMA r_reg COMMA r_reg
                | OR r_reg COMMA r_reg COMMA r_reg
                | XOR r_reg COMMA r_reg COMMA r_reg
                | AND r_reg COMMA r_reg COMMA r_reg
    '''

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
    _instructions.append(insn)

    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_addi(p):
    'insn_addi : ADDI r_reg COMMA r_reg COMMA imm'
    insn0 = Instruction(InsnName.LDI, rd=p[2], imm=p[6])
    # logger_yacc.debug('Insn 0: {}'.format(insn0))
    insn1 = Instruction(InsnName.ADD, rd=p[2], rs=p[4], rt=p[2])
    # logger_yacc.debug('Insn 1: {}'.format(insn1))
    _instructions.append(insn0)
    _instructions.append(insn1)
    p[0] = [insn0, insn1]

    logger_yacc.info("Insn added: {}, {}".format(insn0, insn1))


def p_insn_smis(p):
    'insn_smis : SMIS s_reg COMMA s_mask'

    insn = Instruction(InsnName.SMIS, si=p[2], sq_list=p[4])
    _instructions.append(insn)
    p[0] = insn
    logger_yacc.info("Insn added: {}".format(p[0]))


def p_insn_smit(p):
    'insn_smit : SMIT t_reg COMMA t_mask'

    insn = Instruction(InsnName.SMIT, ti=p[2], tq_list=p[4])
    _instructions.append(insn)
    p[0] = insn
    logger_yacc.info("Insn added: {}".format(p[0]))


# --------------------------- parsing elements ----------------------------


def p_r_reg(p):
    'r_reg : RREG'
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

    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        # p[0] = list(p[1]).append(p[3])
        p[1].append(p[3])
        p[0] = p[1]
    logger_yacc.debug("single_qubit_list: {}".format(p[0]))


def p_s_mask(p):
    's_mask : LBRACE single_qubit_list RBRACE'

    p[0] = p[2]
    logger_yacc.debug("s_mask: {}".format(p[0]))


def p_qubit_pair(p):
    '''qubit_pair : LPAREN INTEGER COMMA INTEGER RPAREN'''

    # pycactus_debug('p_qubit_pair:', end='')

    p[0] = (p[2], p[4])
    logger_yacc.debug("qubit_pair: {}".format(p[0]))


def p_two_qubit_list(p):
    '''two_qubit_list : qubit_pair
                      | two_qubit_list COMMA　qubit_pair
    '''
    # pycactus_debug('p_two_qubit_list:', end='')

    if (len(p) == 2):
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]
    logger_yacc.debug("two_qubit_list: {}".format(p[0]))


def p_t_mask(p):
    't_mask : LBRACE two_qubit_list RBRACE'

    p[0] = p[2]
    logger_yacc.debug("t_mask: {}".format(p[0]))


def p_imm(p):
    '''imm : INTEGER
    '''

    p[0] = p[1]
    logger_yacc.debug("imm: {}".format(p[0]))


def p_label_decl(p):
    'label_decl : IDENTIFIER COLON'

    label = p[1]
    _label_addr[label] = len(_instructions)
    logger_yacc.info("found label: {}".format(label))
    logger_yacc.info("_label_addr: {}".format(_label_addr))
    p[0] = label


def p_offset_to_label(p):
    'offset_to_label : IDENTIFIER'

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

    p[0] = p[1]
    logger_yacc.info("condition: {}".format(p[0]))


def p_error(p):
    print("Syntax error found: {}".format(p))

# --------------------------- end of Parser -----------------------------------


start = 'root'
parser = yacc.yacc(debug=True)

eqasm_dir = pycactus_root_dir / 'tests' / 'eqasm'
custom_file = eqasm_dir / 'custom.eqasm'
# custom_file = eqasm_dir / 'smit.eqasm'
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


result = parser.parse(data.lower(), tracking=True)
logger_yacc.info("all labels: ", _label_addr)
# print(result)
