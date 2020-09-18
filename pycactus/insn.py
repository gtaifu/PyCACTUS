from enum import Enum, auto
from pycactus.utils import *

logger = get_logger(__file__)
# logger.setLevel(logging.DEBUG)


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

    LDUI = auto()  # LDUI Rd, Rs, imm15

    LW = auto()    # LD Rd, Rt(imm10) one imm, one src GPR, one dst GPR
    LB = auto()
    LBU = auto()
    SB = auto()
    SW = auto()


three_reg_cl_insn = {
    InsnName.ADD: "add",
    InsnName.SUB: "sub",
    InsnName.AND: "and",
    InsnName.OR: "or",
    InsnName.XOR: "xor"
}

CMP_FLAG = {'ALWAYS': 0,
            'NEVER': 1,
            'EQ': 2,
            'NE': 3,
            'LTU': 4,
            'GEU': 5,
            'LEU': 6,
            'GTU': 7,
            'LT': 8,
            'GE': 9,
            'LE': 10,
            'GT': 11
            }


class Instruction():
    def __init__(self, name=InsnName.NOP, **kwargs):
        logger.debug(
            "constructing instruction: {} {}".format(name, str(kwargs)))
        self.labels = []  # labels pointing to this instruction
        self.name = name
        self.rd = kwargs.pop('rd', None)
        self.rs = kwargs.pop('rs', None)
        self.rt = kwargs.pop('rt', None)
        self.labels = kwargs.pop('labels', None)
        self.target_label = kwargs.pop('target_label', None)
        self.cmp_flag = kwargs.pop('cmp_flag', None)

        # integer format.
        # the bit length should be checked when generating this instruction
        self.imm = kwargs.pop('imm', None)

        # fields for smit/smit
        self.qs = kwargs.pop('qi', None)
        self.si = kwargs.pop('si', None)
        self.ti = kwargs.pop('ti', None)
        self.sq_list = kwargs.pop('sq_list', None)
        self.tq_list = kwargs.pop('tq_list', None)

        # use to store quantum bundles
        self.op_tr_pair = []  # list of (operation, target reg) pairs
        # logger.debug("constructed the instruction: " + self.__str__())

    def __str__(self):
        if self.name in [InsnName.ADD, InsnName.SUB, InsnName.AND, InsnName.OR, InsnName.XOR]:
            return "{} r{}, r{}, r{}".format(three_reg_cl_insn[self.name], self.rd,
                                             self.rs, self.rt)

        if self.name == InsnName.LDI:
            return "LDI r{}, {}".format(self.rd, self.imm)

        if self.name == InsnName.LDUI:
            return "LDUI r{}, r{}, {}".format(self.rd, self.rs, self.imm)
        if self.name == InsnName.SMIS:
            return "SMIS s{}, {}".format(self.si, self.sq_list)
        if self.name == InsnName.SMIT:
            return "SMIT t{}, {}".format(self.ti, self.tq_list)
        else:
            return "{}".format(self.name)

    # def is_classical(self):
    #     return self.insn_type == InsnType.CLASSICAL

    # def is_quantum(self):
    #     return self.insn_type == InsnType.QUANTUM
