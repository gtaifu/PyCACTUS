import operator
from enum import Enum, auto
from pycactus.utils import *

logger = get_logger((__name__).split('.')[-1])
logger.setLevel(logging.INFO)


class InsnType(Enum):
    UNDEFINED = 0
    CLASSICAL = 1
    QUANTUM = 2


class InsnName(Enum):
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


int_arith_name = {
    InsnName.ADD: "add",
    InsnName.SUB: "sub",
    InsnName.AND: "and",
    InsnName.OR: "or",
    InsnName.XOR: "xor",
    InsnName.MUL: "mul",
    InsnName.DIV: "div",
    InsnName.REM: "rem"
}

int_op = {
    InsnName.ADD: operator.add,
    InsnName.SUB: operator.sub,
    InsnName.AND: operator.and_,
    InsnName.OR: operator.or_,
    InsnName.XOR: operator.xor,
    InsnName.MUL: operator.mul,
    InsnName.DIV: operator.truediv,
    InsnName.REM: operator.mod
}

inv_int_arith_name = {v: k for k, v in int_arith_name.items()}

fp_arith_name = {
    InsnName.FADD_S: "fadd.s",
    InsnName.FSUB_S: "fsub.s",
    InsnName.FMUL_S: "fmul.s",
    InsnName.FDIV_S: "fdiv.s"
}

inv_fp_arith_name = {v: k for k, v in fp_arith_name.items()}

fp_cmp_insn = {
    InsnName.FEQ_S: "feq.s",
    InsnName.FLT_S: "flt.s",
    InsnName.FLE_S: "fle.s"
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
    def __init__(self, name=InsnName.NOP, **kwargs):
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
        if name == InsnName.BUNDLE:
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

    def __str__(self):
        str_labels = " ".join([label + ': ' for label in self.labels])
        return str_labels + self.insn_str()

    def insn_str(self):
        if self.name == InsnName.NOP:
            return 'NOP'

        elif self.name == InsnName.STOP:
            return 'STOP'

        elif self.name == InsnName.QWAIT:
            return "QWAIT {}".format(self.imm)
        elif self.name == InsnName.QWAITR:
            return "QWAITR r{}".format(self.rs)

        elif (self.name == InsnName.BUNDLE):
            return '{}, {}'.format(self.pi, ' | '.join([str(q_op) for q_op in self.q_ops]))

        elif self.name == InsnName.SMIS:
            return "SMIS s{}, {}".format(self.si, self.sq_list)

        elif self.name == InsnName.SMIT:
            return "SMIT t{}, {}".format(self.ti, self.tq_list)

        elif self.name == InsnName.NOT:
            return 'NOT r{}, r{}'.format(self.rd, self.rt)

        elif self.name == InsnName.CMP:  # CMP Rs, Rt
            return 'CMP r{}, r{}'.format(self.rs, self.rt)

        elif self.name == InsnName.BR:
            return 'BR {}, {}'.format(self.cmp_flag.upper(), self.target_label)

        elif self.name == InsnName.FBR:  # FBR <cmp_flag>, Rd
            print('rd type: ', type(self.rd))
            return 'FBR {}, r{}'.format(self.cmp_flag.upper(), self.rd)

        elif self.name == InsnName.FMR:  # FMR rd, qs
            return 'FMR r{}, q{}'.format(self.rd, self.qs)

        elif self.name == InsnName.LDI:
            return "LDI r{}, {}".format(self.rd, self.imm)

        elif self.name in [InsnName.ADD, InsnName.SUB, InsnName.AND, InsnName.OR, InsnName.XOR, InsnName.MUL, InsnName.DIV, InsnName.REM]:
            return "{} r{}, r{}, r{}".format(int_arith_name[self.name].upper(), self.rd,
                                             self.rs, self.rt)

        elif self.name == InsnName.LDUI:
            return "LDUI r{}, r{}, {}".format(self.rd, self.rs, self.imm)

        elif self.name == InsnName.SW or self.name == InsnName.SB:
            return "{} r{}, {}(r{})".format(str(self.name)[-2:], self.rs,
                                            self.imm, self.rt)

        elif (self.name == InsnName.LB or self.name == InsnName.LW
                or self.name == InsnName.LBU):
            return "{} r{}, {}(r{})".format(self.name, self.rd,
                                            self.imm, self.rt)

        elif self.name == InsnName.FCVT_W_S:  # FCVT.W.S rd, fs
            return "FCVT.W.S r{}, f{}".format(self.rd, self.fs)

        elif self.name == InsnName.FCVT_S_W:  # FCVT.S.W fd, rs
            return "FCVT.S.W f{}, r{}".format(self.fd, self.rs)

        elif self.name == InsnName.FLW:
            return "FLW f{}, {}(r{})".format(self.fd, self.imm, self.rs)

        elif self.name == InsnName.FSW:
            return "FSW f{}, {}(r{})".format(self.fs, self.imm, self.rs)

        elif self.name in [InsnName.FADD_S, InsnName.FSUB_S, InsnName.FMUL_S, InsnName.FDIV_S]:
            return "{} f{}, f{}, f{}".format(fp_arith_name[self.name].upper(), self.fd,
                                             self.fs, self.ft)

        elif self.name in [InsnName.FEQ_S, InsnName.FLT_S, InsnName.FLE_S]:
            return "{} r{}, f{}, f{}".format(fp_cmp_insn[self.name].upper(), self.rd,
                                             self.fs, self.ft)
        else:
            return "{}".format(self.name)
