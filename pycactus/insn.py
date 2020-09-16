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
    QWAIT = auto()  # one imm
    QWAITR = auto()  # one GPR

    # two operands
    # one src GPR, one dst GPR
    NOT = auto()  # NOT Rd, Rt

    # two src GPR
    CMP = auto()  # CMP Rs, Rt

    BR = auto()   # BR <cmp_flag>, <label>
    FBR = auto()  # FBR <cmp_flag>, Rd
    FMR = auto()  # FMR Rd, Qi

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
    def __init__(self, **kwargs):
        # self.insn_type = kwargs.pop('type', InsnType.UNDEFINED)
        self.labels = []  # labels pointing to this instruction
        self.name = kwargs.pop('name', InsnName.NOP)
        self.rd = kwargs.pop('rd', None)
        self.rs = kwargs.pop('rs', None)
        self.rt = kwargs.pop('rt', None)
        self.qi = kwargs.pop('qi', None)
        self.labels = kwargs.pop('labels', None)
        self.target_label = kwargs.pop('target_label', None)
        self.cmp_flag = kwargs.pop('cmp_flag', None)

        # integer format.
        # the bit length should be checked when generating this instruction
        self.imm = kwargs.pop('imm', None)
        logger.debug("constructed the instruction: " + self.__str__())

    def __str__(self):
        if self.name in [InsnName.ADD, InsnName.SUB, InsnName.AND, InsnName.OR, InsnName.XOR]:
            return "{} r{}, r{}, r{}".format(three_reg_cl_insn[self.name], self.rd,
                                             self.rs, self.rt)

        if self.name == InsnName.LDI:
            return "LDI r{}, {}".format(self.rd, self.imm)

        if self.name == InsnName.LDUI:
            return "LDUI r{}, r{}, {}".format(self.rd, self.rs, self.imm)

        else:
            return "{}".format(self.name)

    # def is_classical(self):
    #     return self.insn_type == InsnType.CLASSICAL

    # def is_quantum(self):
    #     return self.insn_type == InsnType.QUANTUM
