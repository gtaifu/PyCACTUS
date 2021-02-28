import ply.lex as lex
import logging

from pycactus.utils import get_logger
logger_lex = get_logger('lexer')
logger_lex.setLevel(logging.INFO)


class Eqasm_lexer(object):
    def __init__(self):
        """Create a ply lexer."""
        self.lexer = lex.lex(module=self, debug=False,
                             errorlog=lex.NullLogger())

        self.lineno = 1

    # must be defined for the lexer
    def input(self, data):
        """Set the input text data."""
        self.data = data.lower()
        self.lexer.input(self.data)

    # must be defined for the lexer
    def token(self):
        """Return the next token."""
        ret = self.lexer.token()
        return ret

    reserved = {
        'nop': 'NOP',
        'stop': 'STOP',
        'dumpmem': 'DUMPMEM',
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
        'mul': 'MUL',
        'div': 'DIV',
        'rem': 'REM',
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
        'fmv.w.x': 'FMV_W_X',
        'fmv.x.w': 'FMV_X_W',
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
        # 'SQUOTE',
        'COLON',
        'NEWLINE',
        'HEX',
        'BINARY',
        'DECIMAL',
        'IDENTIFIER',
        'RREG',
        'FREG',
        'SREG',
        'TREG',
        'QREG',
        'VBAR', 'STRING'
    ] + list(reserved.values())

    # Regular expression rules for simple tokens
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_COLON = r":"
    t_VBAR = r'\|'
    # t_SQUOTE = r"'"

    def t_HEX(self, t):
        r'0x[0-9a-fA-F]+'
        # t.type = 'DECIMAL'
        logger_lex.debug('lex: [hex string: {}, value: {}]'.format(
            t.value, int(t.value, base=16)))
        t.value = int(t.value, base=16)
        return t

    def t_BINARY(self, t):
        r'0b[01]+'
        # t.type = 'DECIMAL'
        logger_lex.debug('lex: [bin string: {}, value: {}]'.format(
            t.value, int(t.value, base=2)))
        t.value = int(t.value, base=2)
        return t

    def t_DECIMAL(self, t):
        r'[-]?\d+'
        t.value = int(t.value)
        logger_lex.debug('lex: [DECIMAL string: {}, value: {}]'.format(
            t.value, int(t.value)))

        return t

    def t_COMMA(self, t):
        r","
        return t

    def t_RREG(self, t):
        r'r\d+'
        t.type = 'RREG'
        logger_lex.debug('lex: [RREG: {}, value: {}]'.format(
            t.value, int(t.value[1:])))
        t.value = int(t.value[1:])
        return t  # if no return, this token is thrown away

    def t_FReg(self, t):
        r'f\d+'
        t.type = 'FREG'
        logger_lex.debug('lex: [FReg: {}, value: {}]'.format(
            t.value, int(t.value[1:])))
        t.value = int(t.value[1:])

        return t

    def t_QReg(self, t):
        r'q\d+'
        t.type = 'QREG'
        logger_lex.debug('lex: [QReg: {}, value: {}]'.format(
            t.value, int(t.value[1:])))
        t.value = int(t.value[1:])

        return t

    def t_SReg(self, t):
        r's\d+'
        t.type = 'SREG'
        logger_lex.debug('lex: [SReg: {}, value: {}]'.format(
            t.value, int(t.value[1:])))
        t.value = int(t.value[1:])
        return t

    def t_TReg(self, t):
        r't\d+'
        t.type = 'TREG'
        logger_lex.debug('lex: [TReg: {}, value: {}]'.format(
            t.value, int(t.value[1:])))
        t.value = int(t.value[1:])
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][\.a-zA-Z_0-9]*'
        # Check for reserved words
        # print('found token: {}'.format(t.value))
        t.type = self.reserved.get(t.value, 'IDENTIFIER')
        # print('token type: {}'.format(t.type))
        logger_lex.debug('lex: [{}: {}]'.format(t.type, t.value))
        return t

    def t_STRING(self, t):
        r"'[a-zA-Z0-9 \[\]\(\),]+'"
        t.value = t.value[1:-1]
        return t

    def t_NEWLINE(self, t):
        r'\n'
        self.lineno += len(t.value)
        t.lexer.lineno = self.lineno
        return t

    # def t_eof(t):
    #     t.type = 'NEWLINE'
    #     return t

    t_ignore = ' \t'
    t_ignore_COMMENT = r'\#.*'

    def find_column(self, token):
        """Compute the column.

        Input is the input text string.
        token is a token instance.
        """
        if token is None:
            return 0
        last_line_end = self.data.rfind('\n', 0, token.lexpos)
        column = (token.lexpos - last_line_end)
        return column

    def t_error(self, t):
        raise ValueError("Give string ({}) at (line {}, col {}) cannot match any token rule".format(
            t.value[0], t.lexer.lineno, self.find_column(t)))
        t.lexer.skip(1)

    def build(self, **kwargs):
        '''Build the lexer for eQASM'''
        self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
    def test(self, data):
        self.data = data.lower()
        self.lexer.input(self.data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            # print(tok)
