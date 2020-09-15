from bitstring import BitArray, BitStream
from enum import Enum, auto
from pycactus.utils import *

SIZE_INSN_MEM = 1000000  # accept up to 1 million instructions.
NUM_GPR = 32
GPR_WIDTH = 32

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


class Sq_register():
    def __init__(self, max_num_qubit):
        self._qubits = []
        self._max_num_qubit = max_num_qubit

    def __getitem__(self, item):
        """Return indexed operation."""
        return self._qubits[item]

    def __len__(self):
        """Return number of qubit pairs in this single-qubit target register."""
        return len(self._qubits)

    def append(self, qubit):
        assert(isinstance(qubit, int))

        if qubit not in self._qubits:
            if self.__len__() >= self.max_num_qubit:
                raise ValueError("The sq_register is already full (with {} elements).".format(
                    self.max_num_qubit))
            else:
                self._qubits.append(qubit)


class Tq_register():
    def __init__(self, max_num_qubit_pair: int):
        self._qubit_pairs = []
        self._max_num_qubit_pair = max_num_qubit_pair

    def __getitem__(self, item):
        """Return indexed operation."""
        return self._qubit_pairs[item]

    def __len__(self):
        """Return number of qubit pairs in this two-qubit target register."""
        return len(self._qubit_pairs)

    def append(self, qubit_pair):
        assert(isinstance(qubit_pair, tuple))
        assert(len(qubit_pair) == 2)

        if qubit_pair not in self._qubit_pairs:
            if self.__len__() >= self._max_num_qubit_pair:
                raise ValueError("The tq_register is already full (with {} elements).".format(
                    self._max_num_qubit_pair))
            else:
                self._qubit_pairs.append(qubit_pair)

    # def __iadd__(self, qubit_pair):
    #     """Overload += to implement self.extend."""
    #     return self.append(qubit_pair)


class InsnType(Enum):
    UNDEFINED = 0
    CLASSICAL = 1
    QUANTUM = 2


class InsnName(Enum):
    ADD = auto()
    SUB = auto()
    NOP = auto()
    BR = auto()
    STOP = auto()
    CMP = auto()
    FBR = auto()
    FMR = auto()
    LDI = auto()
    LDUI = auto()
    LD = auto()
    ST = auto()
    OR = auto()
    XOR = auto()
    AND = auto()
    NOT = auto()
    QWAIT = auto()
    QWAITR = auto()


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

        self.insn_mem = []
        self.label_addr = {}
        self.max_insn_num = SIZE_INSN_MEM

        self.pc = start_addr

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

    def process_insn(self, insn):
        print("cycle {}: {}".format(self.cycle, insn))
        if insn.name == InsnName.STOP:
            return False

        elif insn.name == InsnName.NOP:
            pass

        elif insn.name == InsnName.ADD:
            self.gprf[insn.rd].update_value(
                self.gprf[insn.rs] + self.gprf[insn.rt])

        elif insn.name == InsnName.SUB:
            self.gprf[insn.rd].update_value(
                self.gprf[insn.rs] - self.gprf[insn.rt])

        elif insn.name == InsnName.AND:
            self.gprf[insn.rd].update_value(
                self.gprf[insn.rs] & self.gprf[insn.rt])

        elif insn.name == InsnName.OR:
            self.gprf[insn.rd].update_value(
                self.gprf[insn.rs] | self.gprf[insn.rt])

        elif insn.name == InsnName.XOR:
            self.gprf[insn.rd].update_value(
                self.gprf[insn.rs] ^ self.gprf[insn.rt])

        else:
            raise ValueError(
                "Found undefined instruction ({}).".format(insn))

        return True
