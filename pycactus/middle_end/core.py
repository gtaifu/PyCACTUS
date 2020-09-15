from bitstring import BitArray, BitStream
from enum import Enum, auto
from pycactus.utils import *
from pycactus.middle_end.q_pipeline import *

SIZE_INSN_MEM = 1000000  # accept up to 1 million instructions.
NUM_GPR = 32
GPR_WIDTH = 32
NUM_QUBIT = 7

logger = get_logger(__file__)


class General_purpose_register():
    '''General purpose register, used to store integers.
    '''

    def __init__(self, width):
        assert(isinstance(width, int))
        # the width is supposed not to change in the future
        self.bitstring = BitArray(width)
        self._width = width

    def __str__(self):
        return "{}".format(self.bitstring.int)

    def __len__(self):
        return self._width

    def check_length(self, other):
        if self.__len__() != len(other):
            raise ValueError("Cannot perform addition on two bitstring with different"
                             " length ({}, {})".format(self.__len__(), len(other)))

    def __add__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint + other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __not__(self):
        return ~self.bitstring

    def __sub__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint + (~other.bitstring).uint + 1
        return BitArray(uint=unsigned_sum, length=self._width)

    def __and__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint & other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __or__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint | other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __xor__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint ^ other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __eq__(self, other):
        self.check_length(other)
        return self.bitstring == other.bitstring

    def __ne__(self, other):
        self.check_length(other)
        return self.bitstring != other.bitstring

    def update_value(self, value):

        if isinstance(value, int):
            self.bitstring = BitArray(int=value, length=self._width)

        elif isinstance(value, BitArray):
            if self._width != len(value):
                raise ValueError("Given value has a bitstring with a different length ({}) "
                                 " to the original length ({})".format(len(value), self._width))

            self.bitstring = value
        else:
            raise ValueError(
                "Undefined type ({}) is used to update the GPR.".format(type(value)))


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

    LDUI = auto()  # one imm, one src GPR, one dst GPR

    LD = auto()    # LD Rd, Rt(imm10) one imm, one src GPR, one dst GPR
    ST = auto()


three_reg_cl_insn = {
    InsnName.ADD: "add",
    InsnName.SUB: "sub",
    InsnName.AND: "and",
    InsnName.OR: "or",
    InsnName.XOR: "xor"
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
        self.label = kwargs.pop('label', None)
        self.comp_flag = kwargs.pop('comp_flag', None)
        # integer format.
        # the bit length should be checked when generating this instruction
        self.imm = kwargs.pop('imm', None)

    def __str__(self):
        if self.name in [InsnName.ADD, InsnName.SUB, InsnName.AND, InsnName.OR, InsnName.XOR]:
            return "{} r{}, r{}, r{}".format(three_reg_cl_insn[self.name], self.rd,
                                             self.rs, self.rt)

        else:
            return "{}".format(self.name)

    # def is_classical(self):
    #     return self.insn_type == InsnType.CLASSICAL

    # def is_quantum(self):
    #     return self.insn_type == InsnType.QUANTUM


class CMP_FLAG(Enum):
    ALWAYS = 0
    NEVER = 1
    EQ = auto()
    NE = auto()
    LTU = auto()
    GEU = auto()
    LEU = auto()
    GTU = auto()
    LT = auto()
    GE = auto()
    LE = auto()
    GT = auto()


class Quantum_control_processor():
    def __init__(self, start_addr=0):
        self.gprf = []
        for i in range(NUM_GPR):
            self.gprf.append(General_purpose_register(GPR_WIDTH))

        self.fprf = None
        # single-qubit operation target register file
        self.sqotrf = Sq_register(32)
        # two-qubit operation target register file
        self.tqotrf = Tq_register(32)

        # instruction memory
        self.insn_mem = []
        self.label_addr = {}
        self.max_insn_num = SIZE_INSN_MEM

        # qubit measurement result
        self.msmt_result = [0] * NUM_QUBIT

        self.pc = start_addr

        # comparison flags
        self.cmp_flags = [True] + [False] * (len(CMP_FLAG) - 1)

        self.cycle = 0

    def append_insn(self, insn):
        self.insn_mem.append(insn)
        for label in insn.labels:
            if label in self.label_addr:
                raise ValueError(
                    "Found multiple definitions for the same label ({})".format(label))

            self.label_addr[label] = len(self.insn_mem) - 1

    def print_gprf(self):
        for i, gpr in enumerate(self.gprf):
            print('{:>15}'.format('r'+str(i) + ': ' + str(gpr)), end='  ')
            if i % 8 == 7:
                print('')

    def run(self):

        while (True):
            self.cycle += 1

            program_counter = self.pc
            insn = self.insn_mem[program_counter]

            if not self.process_insn(insn):
                break

            # update the PC
            self.pc += 1
            self.print_gprf()

    def update_reg(self, rd, value):
        '''Update the target register `rd` with the `value`
        '''
        self.gprf[rd].update_value(value)

    def process_insn(self, insn):
        print("cycle {}: {}".format(self.cycle, insn))
        # ------------------------- no operand -------------------------
        if insn.name == InsnName.STOP:
            return False

        elif insn.name == InsnName.NOP:
            pass

        # ------------------------- one operand -------------------------
        elif insn.name == InsnName.QWAIT:
            pass

        elif insn.name == InsnName.QWAITR:
            pass

        # ------------------------- two operands -------------------------
        elif insn.name == InsnName.NOT:
            self.update_reg(insn.rd, ~self.gprf[insn.rt])

        elif insn.name == InsnName.CMP:
            self.cmp_flags[CMP_FLAG.EQ] = (
                self.gprf[insn.rs] == self.gprf[insn.rt])
            self.cmp_flags[CMP_FLAG.NE] = (
                self.gprf[insn.rs] != self.gprf[insn.rt])
            self.cmp_flags[CMP_FLAG.LTU] = (
                self.gprf[insn.rs].uint < self.gprf[insn.rt].uint)
            self.cmp_flags[CMP_FLAG.GEU] = (
                self.gprf[insn.rs].uint >= self.gprf[insn.rt].uint)
            self.cmp_flags[CMP_FLAG.LEU] = (
                self.gprf[insn.rs].uint <= self.gprf[insn.rt].uint)
            self.cmp_flags[CMP_FLAG.GTU] = (
                self.gprf[insn.rs].uint > self.gprf[insn.rt].uint)
            self.cmp_flags[CMP_FLAG.LT] = (
                self.gprf[insn.rs].int < self.gprf[insn.rt].int)
            self.cmp_flags[CMP_FLAG.GE] = (
                self.gprf[insn.rs].int >= self.gprf[insn.rt].int)
            self.cmp_flags[CMP_FLAG.LE] = (
                self.gprf[insn.rs].int <= self.gprf[insn.rt].int)
            self.cmp_flags[CMP_FLAG.GT] = (
                self.gprf[insn.rs].int > self.gprf[insn.rt].int)

        elif insn.name == InsnName.BR:
            if self.cmp_flags[insn.comp_flag]:
                self.pc = self.label_addr[insn.label]

        elif insn.name == InsnName.FBR:
            self.update_reg(insn.rd, self.cmp_flags[insn.cmp_flag])

        elif insn.name == InsnName.FMR:
            self.update_reg(insn.rd, self.msmt_result[insn.qi])

        elif insn.name == InsnName.LDI:
            self.update_reg(insn.rd, BitArray(int=insn.imm,
                                              length=len(self.gprf[insn.rd])))

        # ------------------------- three operands -------------------------
        elif insn.name == InsnName.ADD:
            self.update_reg(insn.rd,
                            self.gprf[insn.rs] + self.gprf[insn.rt])

        elif insn.name == InsnName.SUB:
            self.update_reg(insn.rd,
                            self.gprf[insn.rs] - self.gprf[insn.rt])

        elif insn.name == InsnName.AND:
            self.update_reg(insn.rd,
                            self.gprf[insn.rs] & self.gprf[insn.rt])

        elif insn.name == InsnName.OR:
            self.update_reg(insn.rd,
                            self.gprf[insn.rs] | self.gprf[insn.rt])

        elif insn.name == InsnName.XOR:
            self.update_reg(insn.rd,
                            self.gprf[insn.rs] ^ self.gprf[insn.rt])

        elif insn.name == InsnName.LDUI:
            self.update_reg(insn.rd, BitArray(int=insn.imm,
                                              length=len(self.gprf[insn.rd])))
            self.gprf[insn.rd].bitstring[]
        else:
            raise ValueError(
                "Found undefined instruction ({}).".format(insn))

        return True
