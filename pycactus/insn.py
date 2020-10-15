import operator
from enum import Enum, auto

from bitstring import Error
from pycactus.utils import *

logger = get_logger((__name__).split('.')[-1])
logger.setLevel(logging.INFO)


class InsnType(Enum):
    UNDEFINED = 0
    CLASSICAL = 1
    QUANTUM = 2


class eqasm_insn(Enum):
    # no operand
    NOP = auto()
    STOP = auto()

    # one operand
    QWAIT = auto()  # qwait imm
    QWAITR = auto()  # qwaitr rs
    BUNDLE = auto()  # quantum bundles 1, op1 (s/t)reg1 | op2 (s/t)reg2
    SMIS = auto()
    SMIT = auto()

    # two operands
    # one src GPR, one dst GPR
    NOT = auto()  # NOT Rd, Rt

    # two src GPR
    CMP = auto()  # CMP Rs, Rt

    BR = auto()   # BR <cmp_flag>, <label>
    FBR = auto()  # FBR <cmp_flag>, Rd
    FMR = auto()  # fmr rd, qs

    LDI = auto()  # LDI Rd, Imm20

    # three operands
    ADD = auto()  # two src, one dst
    SUB = auto()
    OR = auto()
    XOR = auto()
    AND = auto()
    MUL = auto()
    DIV = auto()
    REM = auto()

    LDUI = auto()  # LDUI Rd, Rs, imm15
    ADDI = auto()  # ADDI Rd, Rs, imm

    LW = auto()    # LD Rd, Rt(imm10) one imm, one src GPR, one dst GPR
    LB = auto()
    LBU = auto()
    SB = auto()
    SW = auto()

    FCVT_W_S = auto()  # FCVT.W.S rd, fs
    FCVT_S_W = auto()  # FCVT.S.W fd, rs
    FLW = auto()       # FLW fd, imm(rs)
    FSW = auto()       # FSW fs, imm(rs)
    FADD_S = auto()    # FADD.S fd, fs1, fs2
    FSUB_S = auto()    # FSUB.S fd, fs1, fs2
    FMUL_S = auto()    # FMUL.S fd, fs1, fs2
    FDIV_S = auto()    # FDIV.S fd, fs1, fs2
    FEQ_S = auto()     # FEQ.S rd, fs1, fs2
    FLT_S = auto()     # FLT.S rd, fs1, fs2
    FLE_S = auto()     # FLE.S rd, fs1, fs2


eqasm_insn_fields = {
    # no operand
    eqasm_insn.NOP: [],
    eqasm_insn.STOP: [],

    # one operand
    eqasm_insn.QWAIT: ['imm'],  # qwait imm
    eqasm_insn.QWAITR: ['rs'],  # qwaitr rs
    # quantum bundles 1, op1 (s/t)reg1 | op2 (s/t)reg2
    eqasm_insn.BUNDLE: ['q_ops'],
    eqasm_insn.SMIS: ['si', 'sq_list'],  # smis si, sq_list
    eqasm_insn.SMIT: ['ti', 'tq_list'],

    # two operands
    # one src GPR, one dst GPR
    eqasm_insn.NOT: ['rd', 'rt'],  # NOT Rd, Rt

    # two src GPR
    eqasm_insn.CMP: ['rs', 'rt'],  # CMP Rs, Rt

    # BR <cmp_flag>, <target_label>
    eqasm_insn.BR: ['cmp_flag', 'target_label'],
    eqasm_insn.FBR: ['cmp_flag', 'rd'],  # FBR <cmp_flag>, Rd
    eqasm_insn.FMR: ['rd', 'qs'],  # fmr rd, qs

    eqasm_insn.LDI: ['rd', 'imm'],  # LDI Rd, Imm20

    # three operands
    eqasm_insn.ADD: ['rd', 'rs', 'rt'],  # ADD rd, rs, rt
    eqasm_insn.SUB: ['rd', 'rs', 'rt'],  # SUB rd, rs, rt
    eqasm_insn.OR: ['rd', 'rs', 'rt'],   # OR  rd, rs, rt
    eqasm_insn.XOR: ['rd', 'rs', 'rt'],  # XOR rd, rs, rt
    eqasm_insn.AND: ['rd', 'rs', 'rt'],  # AND rd, rs, rt
    eqasm_insn.MUL: ['rd', 'rs', 'rt'],  # MUL rd, rs, rt
    eqasm_insn.DIV: ['rd', 'rs', 'rt'],  # DIV rd, rs, rt
    eqasm_insn.REM: ['rd', 'rs', 'rt'],  # REM rd, rs, rt

    eqasm_insn.LDUI: ['rd', 'rs', 'imm'],  # LDUI rd, rs, imm15
    eqasm_insn.ADDI: ['rd', 'rs', 'imm'],  # ADDI Rd, Rs, imm

    eqasm_insn.LW: ['rd', 'imm', 'rt'],    # LD  rd, imm10(rt)
    eqasm_insn.LB: ['rd', 'imm', 'rt'],    # LB  rd, imm10(rt)
    eqasm_insn.LBU: ['rd', 'imm', 'rt'],   # LBU rd, imm10(rt)
    eqasm_insn.SB: ['rs', 'imm', 'rt'],    # SB  rs, imm10(rt)
    eqasm_insn.SW: ['rs', 'imm', 'rt'],    # SW  rs, imm10(rt)

    eqasm_insn.FCVT_W_S: ['rd', 'fs'],        # FCVT.W.S rd, fs
    eqasm_insn.FCVT_S_W: ['fd', 'rs'],        # FCVT.S.W fd, rs
    eqasm_insn.FLW: ['fd', 'imm', 'rs'],      # FLW fd, imm(rs)
    eqasm_insn.FSW: ['fs', 'imm', 'rs'],      # FSW fs, imm(rs)
    eqasm_insn.FADD_S: ['fd', 'fs', 'ft'],  # FADD.S fd, fs, ft
    eqasm_insn.FSUB_S: ['fd', 'fs', 'ft'],  # FSUB.S fd, fs, ft
    eqasm_insn.FMUL_S: ['fd', 'fs', 'ft'],  # FMUL.S fd, fs, ft
    eqasm_insn.FDIV_S: ['fd', 'fs', 'ft'],  # FDIV.S fd, fs, ft
    eqasm_insn.FEQ_S: ['rd', 'fs', 'ft'],   # FEQ.S rd, fs, ft
    eqasm_insn.FLT_S: ['rd', 'fs', 'ft'],   # FLT.S rd, fs, ft
    eqasm_insn.FLE_S: ['rd', 'fs', 'ft']    # FLE.S rd, fs, ft
}

int_arith_name = {
    eqasm_insn.ADD: "add",
    eqasm_insn.SUB: "sub",
    eqasm_insn.AND: "and",
    eqasm_insn.OR: "or",
    eqasm_insn.XOR: "xor",
    eqasm_insn.MUL: "mul",
    eqasm_insn.DIV: "div",
    eqasm_insn.REM: "rem"
}

inv_int_arith_name = {v: k for k, v in int_arith_name.items()}

int_op = {
    eqasm_insn.ADD: operator.add,
    eqasm_insn.SUB: operator.sub,
    eqasm_insn.AND: operator.and_,
    eqasm_insn.OR: operator.or_,
    eqasm_insn.XOR: operator.xor,
    eqasm_insn.MUL: operator.mul,
    eqasm_insn.DIV: operator.truediv,
    eqasm_insn.REM: operator.mod
}

fp_arith_name = {
    eqasm_insn.FADD_S: "fadd.s",
    eqasm_insn.FSUB_S: "fsub.s",
    eqasm_insn.FMUL_S: "fmul.s",
    eqasm_insn.FDIV_S: "fdiv.s"
}

inv_fp_arith_name = {v: k for k, v in fp_arith_name.items()}

fp_op = {
    eqasm_insn.FADD_S: operator.add,
    eqasm_insn.FSUB_S: operator.sub,
    eqasm_insn.FMUL_S: operator.mul,
    eqasm_insn.FDIV_S: operator.truediv
}

fp_cmp_insn = {
    eqasm_insn.FEQ_S: "feq.s",
    eqasm_insn.FLT_S: "flt.s",
    eqasm_insn.FLE_S: "fle.s"
}

fp_cmp_op = {
    eqasm_insn.FEQ_S: operator.eq,
    eqasm_insn.FLT_S: operator.lt,
    eqasm_insn.FLE_S: operator.le
}


inv_fp_cmp_insn = {v: k for k, v in fp_cmp_insn.items()}

CMP_FLAG = {'always': 0,
            'never': 1,
            'eq': 2,
            'ne': 3,
            'ltu': 4,
            'geu': 5,
            'leu': 6,
            'gtu': 7,
            'lt': 8,
            'ge': 9,
            'le': 10,
            'gt': 11
            }

cmp_op = {
    'eq': operator.eq,
    'ne': operator.ne,
    'ltu': operator.lt,
    'geu': operator.ge,
    'leu': operator.le,
    'gtu': operator.ge,
    'lt': operator.lt,
    'ge': operator.ge,
    'le': operator.le,
    'gt': operator.ge
}


class Quantum_op():
    def __init__(self, name='QNOP', **kwargs):
        self.name = name
        self.sreg = kwargs.pop('sreg', None)
        self.treg = kwargs.pop('treg', None)

    def __str__(self):
        if self.sreg is not None:
            return "QOP: [{} s{}]".format(self.name, self.sreg)
        elif self.treg is not None:
            return "QOP: [{} t{}]".format(self.name, self.treg)
        else:
            return self.name


class Instruction():
    def __init__(self, name=eqasm_insn.NOP, **kwargs):
        logger.debug(
            "constructing instruction: {} {}".format(name, str(kwargs)))
        self.name = name
        self.rd = kwargs.pop('rd', None)
        self.rs = kwargs.pop('rs', None)
        self.rt = kwargs.pop('rt', None)
        self.fd = kwargs.pop('fd', None)
        self.fs = kwargs.pop('fs', None)  # fs -> fs1
        self.ft = kwargs.pop('ft', None)  # ft -> fs2
        self.labels = kwargs.pop('labels', [])
        self.target_label = kwargs.pop('target_label', None)
        self.cmp_flag = kwargs.pop('cmp_flag', None)

        # integer format.
        # the bit length should be checked when generating this instruction
        self.imm = kwargs.pop('imm', None)

        # fields for smit/smit
        self.qs = kwargs.pop('qs', None)
        self.si = kwargs.pop('si', None)
        self.ti = kwargs.pop('ti', None)
        self.sq_list = kwargs.pop('sq_list', None)
        self.tq_list = kwargs.pop('tq_list', None)

        # use to store quantum bundles
        self.pi = kwargs.pop('pi', 0)
        if name == eqasm_insn.BUNDLE:
            # list of (operation, target reg) pairs
            q_ops = kwargs.pop('q_ops', None)
            if isinstance(q_ops, Quantum_op):
                self.q_ops = [q_ops]
            elif isinstance(q_ops, list):
                assert(all(isinstance(q_op, Quantum_op) for q_op in q_ops))
            else:
                raise ValueError("Given q_ops ({}) is neither "
                                 "Quantum_op nor list.".format(q_ops))

            self.q_ops = q_ops

        self._check_fields()

    def _check_fields(self):
        'Check if the instruction has already all required fields.'
        required_fields = eqasm_insn_fields[self.name]
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError("The instruction {} does not have the required field '{}'.".format(
                    self.name, field))

    def __str__(self):
        str_labels = " ".join([label + ': ' for label in self.labels])
        return str_labels + self.insn_str()

    def insn_str(self):
        if self.name == eqasm_insn.NOP:
            return 'NOP'

        elif self.name == eqasm_insn.STOP:
            return 'STOP'

        elif self.name == eqasm_insn.QWAIT:
            return "QWAIT {}".format(self.imm)
        elif self.name == eqasm_insn.QWAITR:
            return "QWAITR r{}".format(self.rs)

        elif (self.name == eqasm_insn.BUNDLE):
            return '{}, {}'.format(self.pi, ' | '.join([str(q_op) for q_op in self.q_ops]))

        elif self.name == eqasm_insn.SMIS:
            return "SMIS s{}, {}".format(self.si, self.sq_list)

        elif self.name == eqasm_insn.SMIT:
            return "SMIT t{}, {}".format(self.ti, self.tq_list)

        elif self.name == eqasm_insn.NOT:
            return 'NOT r{}, r{}'.format(self.rd, self.rt)

        elif self.name == eqasm_insn.CMP:  # CMP Rs, Rt
            return 'CMP r{}, r{}'.format(self.rs, self.rt)

        elif self.name == eqasm_insn.BR:
            return 'BR {}, {}'.format(self.cmp_flag.upper(), self.target_label)

        elif self.name == eqasm_insn.FBR:  # FBR <cmp_flag>, Rd
            return 'FBR {}, r{}'.format(self.cmp_flag.upper(), self.rd)

        elif self.name == eqasm_insn.FMR:  # FMR rd, qs
            return 'FMR r{}, q{}'.format(self.rd, self.qs)

        elif self.name == eqasm_insn.LDI:
            return "LDI r{}, {}".format(self.rd, self.imm)

        elif self.name in [eqasm_insn.ADD, eqasm_insn.SUB, eqasm_insn.AND,
                           eqasm_insn.OR, eqasm_insn.XOR, eqasm_insn.MUL,
                           eqasm_insn.DIV, eqasm_insn.REM]:
            return "{} r{}, r{}, r{}".format(int_arith_name[self.name].upper(), self.rd,
                                             self.rs, self.rt)

        elif self.name == eqasm_insn.LDUI:
            return "LDUI r{}, r{}, {}".format(self.rd, self.rs, self.imm)

        elif self.name == eqasm_insn.ADDI:
            return "ADDI r{}, r{}, {}".format(self.rd, self.rs, self.imm)

        elif self.name == eqasm_insn.SW or self.name == eqasm_insn.SB:
            return "{} r{}, {}(r{})".format(str(self.name)[-2:], self.rs,
                                            self.imm, self.rt)

        elif (self.name == eqasm_insn.LB or self.name == eqasm_insn.LW
                or self.name == eqasm_insn.LBU):
            return "{} r{}, {}(r{})".format(self.name, self.rd,
                                            self.imm, self.rt)

        elif self.name == eqasm_insn.FCVT_W_S:  # FCVT.W.S rd, fs
            return "FCVT.W.S r{}, f{}".format(self.rd, self.fs)

        elif self.name == eqasm_insn.FCVT_S_W:  # FCVT.S.W fd, rs
            return "FCVT.S.W f{}, r{}".format(self.fd, self.rs)

        elif self.name == eqasm_insn.FLW:
            return "FLW f{}, {}(r{})".format(self.fd, self.imm, self.rs)

        elif self.name == eqasm_insn.FSW:
            return "FSW f{}, {}(r{})".format(self.fs, self.imm, self.rs)

        elif self.name in [eqasm_insn.FADD_S, eqasm_insn.FSUB_S,
                           eqasm_insn.FMUL_S, eqasm_insn.FDIV_S]:
            return "{} f{}, f{}, f{}".format(fp_arith_name[self.name].upper(), self.fd,
                                             self.fs, self.ft)

        elif self.name in [eqasm_insn.FEQ_S, eqasm_insn.FLT_S, eqasm_insn.FLE_S]:
            return "{} r{}, f{}, f{}".format(fp_cmp_insn[self.name].upper(), self.rd,
                                             self.fs, self.ft)
        else:
            return "{}".format(self.name)
