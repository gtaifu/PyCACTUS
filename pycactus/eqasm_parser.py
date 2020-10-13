# TODO: when is the correct moment to convert immediate value into positive or negative?
# TODO: add definition def_sym and .register

# ------------------------------------------------------------
import logging
from logging import error
import tempfile
from pycactus.eqasm_lexer import Eqasm_lexer
from pycactus.global_config import pycactus_root_dir
from pathlib import Path
import re
import ply.lex as lex
import ply.yacc as yacc
from pycactus.insn import *
from pycactus.utils import get_logger
logger_yacc = get_logger('yacc')
logger_yacc.setLevel(logging.ERROR)


class Eqasm_parser:
    '''eQASM parser'''

    def __init__(self):
        self.lexer = Eqasm_lexer()
        # print("lexer in parser is: ", self.lexer)
        self.tokens = self.lexer.tokens
        self.parse_dir = tempfile.mkdtemp(prefix='pycactus')
        # For yacc, also, write_tables = Bool and optimize = Bool
        self.parser = yacc.yacc(module=self, debug=True,
                                outputdir=self.parse_dir)

        self._instructions = []
        self._label_addr = {}

    # =================================================================================
    # start of the ply parser
    # =================================================================================
    start = 'root'

    def p_root(self, p):
        '''root : program
        '''
        p[0] = p[1]

    def p_program(self, p):
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
        logger_yacc.info("program, _label_addr: {}".format(self._label_addr))

    def p_instruction(self, p):
        '''instruction : NEWLINE
                       | label_decl           NEWLINE
                       | statement            NEWLINE
                       | label_decl statement NEWLINE
        '''
        p[0] = p[1]
        logger_yacc.info(
            "instruction, _label_addr: {}".format(self._label_addr))

    def p_statement(self, p):
        '''statement : classic_statement
                     | quantum_statement
        '''
        p[0] = p[1]

    def p_classic_statement(self, p):
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
                             | insn_fcvtws
                             | insn_fcvtsw
                             | insn_flw
                             | insn_fsw
                             | insn_fp_arith
                             | insn_fcmp
                             | insn_bra
                             | insn_goto
                             | insn_brn
                             | insn_bcond
        '''
        p[0] = p[1]

    def p_insn_fcvtws(self, p):  # FCVT.W.S rd, fs
        'insn_fcvtws : FCVT_W_S r_reg COMMA f_reg'
        insn = Instruction(eqasm_insn.FCVT_W_S, rd=p[2], fs=p[4])
        p[0] = insn
        self._instructions.append(insn)

    def p_insn_fcvtsw(self, p):  # FCVT.S.W fd, rs
        'insn_fcvtsw : FCVT_S_W f_reg COMMA r_reg'
        insn = Instruction(eqasm_insn.FCVT_S_W, fd=p[2], rs=p[4])
        p[0] = insn
        self._instructions.append(insn)

    def p_insn_flw(self, p):
        'insn_flw : FLW f_reg COMMA imm LPAREN r_reg RPAREN'
        insn = Instruction(eqasm_insn.FLW, fd=p[2], imm=p[4], rs=p[6])
        p[0] = insn
        self._instructions.append(insn)

    def p_insn_fsw(self, p):
        'insn_fsw : FSW f_reg COMMA imm LPAREN r_reg RPAREN'
        insn = Instruction(eqasm_insn.FSW, fs=p[2], imm=p[4], rs=p[6])
        p[0] = insn
        self._instructions.append(insn)

    def p_insn_fp_arith(self, p):
        '''insn_fp_arith : FADD_S f_reg COMMA f_reg COMMA f_reg
                         | FSUB_S f_reg COMMA f_reg COMMA f_reg
                         | FMUL_S f_reg COMMA f_reg COMMA f_reg
                         | FDIV_S f_reg COMMA f_reg COMMA f_reg
        '''
        insn_name = inv_fp_arith_name[p[1]]
        insn = Instruction(insn_name, fd=p[2], fs=p[4], ft=p[6])
        p[0] = insn
        self._instructions.append(insn)

    def p_insn_fcmp(self, p):
        '''insn_fcmp : FEQ_S r_reg COMMA f_reg COMMA f_reg
                     | FLT_S r_reg COMMA f_reg COMMA f_reg
                     | FLE_S r_reg COMMA f_reg COMMA f_reg
        '''
        insn_name = inv_fp_cmp_insn[p[1]]
        insn = Instruction(insn_name, rd=p[2], fs=p[4], ft=p[6])
        p[0] = insn
        self._instructions.append(insn)

    def p_quantum_statement(self, p):
        '''quantum_statement : qbs quantum_instructions
                             | quantum_instructions
        '''
        if len(p) == 3:
            bs = p[1]
            q_ops = p[2]
        else:
            bs = 1
            q_ops = p[1]
        insn = Instruction(eqasm_insn.BUNDLE, pi=bs, q_ops=q_ops)
        self._instructions.append(insn)
        p[0] = insn

    def p_insn_nop(self, p):  # nop
        'insn_nop : NOP'

        p[0] = insn = Instruction(eqasm_insn.NOP)
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_stop(self, p):  # stop
        'insn_stop : STOP'

        p[0] = insn = Instruction(eqasm_insn.STOP)
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_qwait(self, p):  # qwait u_imm
        'insn_qwait : QWAIT imm'
        p[0] = insn = Instruction(eqasm_insn.QWAIT, imm=p[2])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_qwaitr(self, p):  # qwaitr rs
        'insn_qwaitr : QWAITR r_reg'
        p[0] = insn = Instruction(eqasm_insn.QWAITR, rs=p[2])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_not(self, p):  # not rd, rt
        'insn_not : NOT r_reg COMMA r_reg'
        p[0] = insn = Instruction(eqasm_insn.NOT, rd=p[2], rt=p[4])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_cmp(self, p):
        'insn_cmp : CMP r_reg COMMA r_reg'
        p[0] = insn = Instruction(eqasm_insn.CMP, rs=p[2], rt=p[4])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_fmr(self, p):  # fmr rd, qs
        'insn_fmr : FMR r_reg COMMA q_reg'

        p[0] = insn = Instruction(eqasm_insn.FMR, rd=p[2], qs=p[4])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_ldi(self, p):  # ldi rd, imm
        'insn_ldi : LDI r_reg COMMA imm'
        p[0] = insn = Instruction(eqasm_insn.LDI, rd=p[2], imm=p[4])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_ldui(self, p):  # ldui rd, rs, u_imm
        '''insn_ldui : LDUI r_reg COMMA r_reg COMMA imm
                     | LDUI r_reg COMMA imm
        '''
        if len(p) == 6:
            rd = p[2]
            rs = p[4]
            imm = p[6]
        else:
            rd = rs = p[2]
            imm = p[4]

        p[0] = insn = Instruction(eqasm_insn.LDUI, rd=rd, rs=rs, imm=imm)

        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_ld(self, p):  # lw/lb/lbu rd, imm10(rt)
        '''insn_ld : LW r_reg COMMA imm LPAREN r_reg RPAREN
                   | LB r_reg COMMA imm LPAREN r_reg RPAREN
                   | LBU r_reg COMMA imm LPAREN r_reg RPAREN
        '''

        if (p[1]).lower() == 'lw':
            insn = Instruction(eqasm_insn.LW, rd=p[2], imm=p[4], rt=p[6])
        elif (p[1]).lower() == 'lb':
            insn = Instruction(eqasm_insn.LB, rd=p[2], imm=p[4], rt=p[6])
        elif (p[1]).lower() == 'lbu':
            insn = Instruction(eqasm_insn.LBU, rd=p[2], imm=p[4], rt=p[6])
        else:
            assert(False)

        self._instructions.append(insn)
        p[0] = insn
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_st(self, p):  # sw/sb rs, imm10(rt)
        '''insn_st : SW r_reg COMMA imm LPAREN r_reg RPAREN
                | SB r_reg COMMA imm LPAREN r_reg RPAREN
        '''

        if (p[1]).lower() == 'sw':
            insn = Instruction(eqasm_insn.SW, rs=p[2], imm=p[4], rt=p[6])
        elif (p[1]).lower() == 'sb':
            insn = Instruction(eqasm_insn.SB, rs=p[2], imm=p[4], rt=p[6])
        else:
            assert(False)
        p[0] = insn
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_br(self, p):
        'insn_br : BR cond COMMA offset_to_label'
        insn = Instruction(eqasm_insn.BR, cmp_flag=p[2],
                           target_label=p[4])
        self._instructions.append(insn)
        p[0] = insn

    def p_insn_bra(self, p):
        '''insn_bra : BRA offset_to_label
        '''
        insn = Instruction(eqasm_insn.BR, cmp_flag='always',
                           target_label=p[2])
        self._instructions.append(insn)
        p[0] = insn

        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_goto(self, p):
        '''insn_goto : GOTO offset_to_label
        '''
        p[0] = insn = Instruction(eqasm_insn.BR, cmp_flag='always',
                                  target_label=p[2])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_brn(self, p):
        '''insn_brn : BRN offset_to_label
        '''
        p[0] = insn = Instruction(eqasm_insn.BR, cmp_flag='never',
                                  target_label=p[2])
        self._instructions.append(insn)
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_bcond(self, p):
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
        insn0 = Instruction(eqasm_insn.CMP, rs=p[2], rt=p[4])
        insn1 = Instruction(eqasm_insn.BR, cmp_flag=p[1][1:],
                            target_label=p[6])
        self._instructions.append(insn0)
        self._instructions.append(insn1)
        p[0] = [insn0, insn1]
        logger_yacc.info("Insn added: {}, {}".format(insn0, insn1))

    def p_insn_fbr(self, p):
        'insn_fbr : FBR cond COMMA r_reg'
        insn = Instruction(eqasm_insn.FBR, cmp_flag=p[2], rd=p[4])
        self._instructions.append(insn)
        p[0] = insn

    def p_insn_rrr(self, p):  # add/sub/or/xor/and  rd, rs, rt
        '''insn_rrr : ADD r_reg COMMA r_reg COMMA r_reg
                    | SUB r_reg COMMA r_reg COMMA r_reg
                    | OR r_reg COMMA r_reg COMMA r_reg
                    | XOR r_reg COMMA r_reg COMMA r_reg
                    | AND r_reg COMMA r_reg COMMA r_reg
                    | MUL r_reg COMMA r_reg COMMA r_reg
                    | DIV r_reg COMMA r_reg COMMA r_reg
                    | REM r_reg COMMA r_reg COMMA r_reg
        '''
        insn_name = inv_int_arith_name[p[1]]
        insn = Instruction(insn_name, rd=p[2], rs=p[4], rt=p[6])
        p[0] = insn
        self._instructions.append(insn)

        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_addi(self, p):
        'insn_addi : ADDI r_reg COMMA r_reg COMMA imm'
        insn0 = Instruction(eqasm_insn.LDI, rd=p[2], imm=p[6])
        # logger_yacc.debug('Insn 0: {}'.format(insn0))
        insn1 = Instruction(eqasm_insn.ADD, rd=p[2], rs=p[4], rt=p[2])
        # logger_yacc.debug('Insn 1: {}'.format(insn1))
        self._instructions.append(insn0)
        self._instructions.append(insn1)
        p[0] = [insn0, insn1]

        logger_yacc.info("Insn added: {}, {}".format(insn0, insn1))

    def p_insn_smis(self, p):
        'insn_smis : SMIS s_reg COMMA s_mask'

        insn = Instruction(eqasm_insn.SMIS, si=p[2], sq_list=p[4])
        self._instructions.append(insn)
        p[0] = insn
        logger_yacc.info("Insn added: {}".format(p[0]))

    def p_insn_smit(self, p):
        'insn_smit : SMIT t_reg COMMA t_mask'

        insn = Instruction(eqasm_insn.SMIT, ti=p[2], tq_list=p[4])
        self._instructions.append(insn)
        p[0] = insn
        logger_yacc.info("Insn added: {}".format(p[0]))

    # ---------------------------------------------------------------------
    # quantum instruction elements
    # ---------------------------------------------------------------------
    def p_qbs(self, p):
        '''qbs : optional_bs INTEGER COMMA
               | optional_bs INTEGER
        '''
        p[0] = p[2]

    def p_optional_bs(self, p):
        '''optional_bs : empty
                    | BS
        '''
        p[0] = None

    def p_quantum_instructions(self, p):
        '''quantum_instructions : quantum_instruction
                                | quantum_instructions VBAR quantum_instruction
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]
        logger_yacc.debug('quantum_instructions: {}'.format(p[0]))

    def p_quantum_instruction(self, p):
        '''quantum_instruction : nq_op
                            | sq_op
                            | tq_op
        '''
        p[0] = p[1]
        logger_yacc.debug('p_quantum_instruction: {}'.format(p[0]))

    def p_nq_op(self, p):
        'nq_op : QNOP'
        p[0] = Quantum_op('QNOP')
        logger_yacc.debug('nq_op: {}'.format(p[0]))

    def p_sq_op(self, p):
        '''sq_op : IDENTIFIER s_reg
        '''
        p[0] = Quantum_op(p[1], sreg=p[2])
        logger_yacc.debug('sq_op: {}'.format(p[0]))

    def p_tq_op(self, p):
        '''tq_op : IDENTIFIER t_reg
        '''
        p[0] = Quantum_op(p[1], treg=p[2])
        logger_yacc.debug('tq_op: {}'.format(p[0]))

    # ---------------------------------------------------------------------
    # parsing elements
    # ---------------------------------------------------------------------
    def p_empty(self, p):
        'empty :'
        pass

    def p_r_reg(self, p):
        'r_reg : RREG'
        p[0] = p[1]

    def p_f_reg(self, p):
        'f_reg : FREG'
        p[0] = p[1]

    def p_q_reg(self, p):
        'q_reg : QREG'
        p[0] = p[1]

    def p_s_reg(self, p):
        's_reg : SREG'
        p[0] = p[1]

    def p_t_reg(self, p):
        't_reg : TREG'
        p[0] = p[1]

    def p_single_qubit_list(self, p):
        '''single_qubit_list : INTEGER
                            | single_qubit_list COMMA INTEGER'''

        if (len(p) == 2):
            p[0] = [p[1]]
        else:
            # p[0] = list(p[1]).append(p[3])
            p[1].append(p[3])
            p[0] = p[1]
        logger_yacc.debug("single_qubit_list: {}".format(p[0]))

    def p_s_mask(self, p):
        's_mask : LBRACE single_qubit_list RBRACE'

        p[0] = p[2]
        logger_yacc.debug("s_mask: {}".format(p[0]))

    def p_qubit_pair(self, p):
        '''qubit_pair : LPAREN INTEGER COMMA INTEGER RPAREN'''

        # pycactus_debug('p_qubit_pair:', end='')

        p[0] = (p[2], p[4])
        logger_yacc.debug("qubit_pair: {}".format(p[0]))

    def p_two_qubit_list(self, p):
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

    def p_t_mask(self, p):
        't_mask : LBRACE two_qubit_list RBRACE'

        p[0] = p[2]
        logger_yacc.debug("t_mask: {}".format(p[0]))

    def p_imm(self, p):
        '''imm : INTEGER
        '''

        p[0] = p[1]
        logger_yacc.debug("imm: {}".format(p[0]))

    def p_label_decl(self, p):
        'label_decl : IDENTIFIER COLON'

        label = p[1]
        self._label_addr[label] = len(self._instructions)
        logger_yacc.info("found label: {}".format(label))
        logger_yacc.info("_label_addr: {}".format(self._label_addr))
        p[0] = label

    def p_offset_to_label(self, p):
        'offset_to_label : IDENTIFIER'

        label = p[1]
        p[0] = label
        logger_yacc.info("target label: {}".format(label))

    def p_cond(self, p):
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

    def p_error(self, p):
        if not p:
            logger_yacc.info("Successfully parsed the entire file.")
            return

        p.lexpos = col = self.find_column(self.lexer.data, p)
        lines = self.lexer.data.split('\n')
        error_msg = "Syntax error: Found unmatched {0}. Skip line {1}:  {2}".format(
            p, self.lexer.lineno, lines[self.lexer.lineno-1])
        self.error_list.append(error_msg)
        logger_yacc.error(error_msg)

        # Read ahead looking for a new line
        while True:
            tok = self.lexer.token()             # Get the next token
            if not tok or tok.type == 'NEWLINE':
                break
        self.parser.restart()

    # =================================================================================
    # end of the parser
    # =================================================================================

    def find_column(self, input_, token):
        """Compute the column.

        Input is the input text string.
        token is a token instance.
        """
        if token is None:
            return 0
        last_line_end = input_.rfind('\n', 0, token.lexpos)
        column = (token.lexpos - last_line_end)
        return column

    def read_tokens(self):
        """finds and reads the tokens."""
        try:
            while True:
                token = self.lexer.token()

                if not token:
                    break

                yield token
        except Exception as e:
            print('Exception in tokenizing a eqasm file:', repr(e))

    def parse(self, data=None, filename=None,  debug=False):
        """Parse some data."""
        if data is None:
            data = Path(filename).read_text()

        self._instructions = []
        self.error_list = []
        self._label_addr = {}
        self.parser.parse(data.lower(), lexer=self.lexer)

        for l in self._label_addr:
            self._instructions[self._label_addr[l]].labels.append(l)

        success = True
        if len(self.error_list) > 0:
            for e in self.error_list:
                logger_yacc.error(e)

            error_msgs = "\n".join(self.error_list)
            print("Found errors in parsing the eqasm file: {}".format(error_msgs))
            success = False

        return success, self._instructions
