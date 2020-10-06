from bitstring import BitArray
from .utils import *
from .qotr import QOTRF
from .insn import *
from .gpr import *
from .memory import Memory
import pycactus.global_config as gc


logger = get_logger(__file__)
# logger.setLevel(logging.DEBUG)


class Quantum_control_processor():
    def __init__(self, start_addr=0):

        self.gprf = GPRF()  # general purpose register file
        self.fprf = None    # floating point register file

        # operation target register files
        self.qotrf = QOTRF()

        self.max_insn_num = gc.SIZE_INSN_MEM
        self.start_addr = start_addr

        # data memory
        self.data_mem = Memory(size=gc.SIZE_DATA_MEM)
        self.reset()

    def reset(self):
        '''Completely reset the QCP state. Except the data memory, all memory is cleaned.
        Should be used before uploading a new program.

        N.B.: we do not need to reset the data memory during the reset process.
        '''
        self.restart()
        # instruction memory
        self.insn_mem = []
        self.label_addr = {}
        # self.num_iteration = 0  # used for debug. TODO: remove after passing the test

    def restart(self):
        '''Restart the program. All architectural states except the instruction memory
        and data memory are reset to the initial state.
        Should be used when restarting the same program.
        '''
        self.stop_bit = 0
        self.cycle = 0
        self.pc = self.start_addr
        # qubit measurement result
        self.msmt_result = [0] * gc.NUM_QUBIT
        # comparison flags
        self.cmp_flags = [True] + [False] * (len(CMP_FLAG) - 1)

    def dump_cmp_flags(self):
        for key in CMP_FLAG:
            print("{:>6}: {}".format(key, int(self.cmp_flags[CMP_FLAG[key]])))

    def upload_program(self, insns):
        assert(all(isinstance(insn, Instruction) for insn in insns))

        if (len(insns) > self.max_insn_num):
            raise ValueError("Given program has a length ({}) exceeds the allowed maximum"
                             " number of instructions ({}).".format(len(insns), self.max_insn_num))

        self.reset()
        self.insn_mem = insns
        self.parse_labels()

    def parse_labels(self):
        self.label_addr = {}
        for i, insn in enumerate(self.insn_mem):
            for label in insn.labels:
                self.label_addr[label] = i

        for insn in self.insn_mem:
            if insn.name in [InsnName.BR]:
                if insn.target_label not in self.label_addr:
                    raise ValueError("Given program is malformed. Cannot find the definition for "
                                     "the target address label: {} in the instruction {}".format(
                                         insn.target_label, insn))

    def append_insn(self, insn):
        self.insn_mem.append(insn)

        for label in insn.labels:
            if label in self.label_addr:
                raise ValueError(
                    "Found multiple definitions for the same label ({})".format(label))

            self.label_addr[label] = len(self.insn_mem) - 1

        logger.debug("insn mem size: {}.".format(len(self.insn_mem)))

    def advance_one_cycle(self):
        self.cycle += 1

        # fetch the instruction
        insn = self.insn_mem[self.pc]
        logger.debug("PC: {}, insn: {}".format(self.pc, insn))

        self.process_insn(insn)  # execute

    def write_gpr(self, rd: int, value: BitArray):
        '''Update the target register `rd` with the `value`
        '''
        if isinstance(value, int):
            value = BitArray(int=value, length=32)
        self.gprf.write(rd, value)

    def read_gpr_unsigned(self, rs: int):
        return self.gprf.read_unsigned(rs)

    def read_gpr_signed(self, rs: int):
        return self.gprf.read_signed(rs)

    def print_gpr(self, rd):
        self.gprf.print_reg(rd)

    def run(self):
        while (self.stop_bit == 0):
            self.advance_one_cycle()

    def process_insn(self, insn):
        print("cycle {}: {}".format(self.cycle, insn))
        # ------------------------- no operand -------------------------
        if insn.name == InsnName.STOP:
            self.stop_bit = 1
            self.pc += 1             # update the PC

        elif insn.name == InsnName.NOP:
            self.pc += 1             # update the PC

        # ------------------------- one operand -------------------------
        elif insn.name == InsnName.QWAIT:
            self.pc += 1             # update the PC

        elif insn.name == InsnName.QWAITR:
            self.pc += 1             # update the PC

        # ------------------------- two operands -------------------------
        elif insn.name == InsnName.NOT:
            assert(insn.rd is not None)
            assert(insn.rt is not None)
            print("~self.gprf[insn.rt]: ", ~self.gprf[insn.rt])
            self.write_gpr(insn.rd, ~self.gprf[insn.rt])
            self.pc += 1             # update the PC

        elif insn.name == InsnName.CMP:
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.cmp_flags[CMP_FLAG['eq']] = (
                self.gprf[insn.rs] == self.gprf[insn.rt])
            self.cmp_flags[CMP_FLAG['ne']] = (
                self.gprf[insn.rs] != self.gprf[insn.rt])
            self.cmp_flags[CMP_FLAG['ltu']] = (
                self.read_gpr_unsigned(insn.rs) < self.read_gpr_unsigned(insn.rt))
            self.cmp_flags[CMP_FLAG['geu']] = (
                self.read_gpr_unsigned(insn.rs) >= self.read_gpr_unsigned(insn.rt))
            self.cmp_flags[CMP_FLAG['leu']] = (
                self.read_gpr_unsigned(insn.rs) <= self.read_gpr_unsigned(insn.rt))
            self.cmp_flags[CMP_FLAG['gtu']] = (
                self.read_gpr_unsigned(insn.rs) > self.read_gpr_unsigned(insn.rt))
            self.cmp_flags[CMP_FLAG['lt']] = (
                self.read_gpr_signed(insn.rs) < self.read_gpr_signed(insn.rt))
            self.cmp_flags[CMP_FLAG['ge']] = (
                self.read_gpr_signed(insn.rs) >= self.read_gpr_signed(insn.rt))
            self.cmp_flags[CMP_FLAG['le']] = (
                self.read_gpr_signed(insn.rs) <= self.read_gpr_signed(insn.rt))
            self.cmp_flags[CMP_FLAG['gt']] = (
                self.read_gpr_signed(insn.rs) > self.read_gpr_signed(insn.rt))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.BR:
            assert(insn.cmp_flag is not None)
            assert(insn.target_label is not None)

            # self.num_iteration += 1
            # if self.num_iteration > 100:
            #     print('The number of iteration has exceeded the maximum allowed number.')
            #     exit(0)
            # print("current flag: ", insn.cmp_flag.upper())
            # print("self.label_addr[insn.target_label]: ",
            #       self.label_addr[insn.target_label])

            if self.cmp_flags[CMP_FLAG[insn.cmp_flag]]:
                print("current PC: ", self.pc)
                self.pc = self.label_addr[insn.target_label]
                print("next pc: ", self.pc)
            else:
                self.pc += 1

        elif insn.name == InsnName.FBR:
            assert(insn.rd is not None)
            assert(insn.cmp_flag is not None)
            self.write_gpr(insn.rd, self.cmp_flags[CMP_FLAG[insn.cmp_flag]])
            self.pc += 1             # update the PC

        elif insn.name == InsnName.FMR:
            assert(insn.rd is not None)
            assert(insn.qs is not None)
            self.write_gpr(insn.rd, self.msmt_result[insn.qs])
            self.pc += 1             # update the PC

        elif insn.name == InsnName.LDI:
            assert(insn.rd is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            self.write_gpr(insn.rd, BitArray(int=insn.imm,
                                             length=len(self.gprf[insn.rd])))

            self.pc += 1             # update the PC

        # ------------------------- three operands -------------------------
        elif insn.name == InsnName.ADD:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.write_gpr(insn.rd, self.gprf[insn.rs] + self.gprf[insn.rt])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.SUB:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.write_gpr(insn.rd, self.gprf[insn.rs] - self.gprf[insn.rt])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.AND:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.write_gpr(insn.rd, self.gprf[insn.rs] & self.gprf[insn.rt])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.OR:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.write_gpr(insn.rd, self.gprf[insn.rs] | self.gprf[insn.rt])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.XOR:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            self.write_gpr(insn.rd, self.gprf[insn.rs] ^ self.gprf[insn.rt])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.LDUI:
            assert(insn.rd is not None)
            assert(insn.rs is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as unsigned integer
            composed_bitstring = BitArray(
                uint=insn.imm, length=15) + self.gprf[insn.rs][15:32]
            self.write_gpr(insn.rd, composed_bitstring)

            self.pc += 1             # update the PC

        elif insn.name == InsnName.LW:
            assert(insn.rd is not None)
            assert(insn.rt is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rt) + insn.imm
            ret_word = self.data_mem.read_word(addr)
            self.write_gpr(insn.rd, ret_word)

            self.pc += 1             # update the PC

        elif insn.name in [InsnName.LB, InsnName.LBU]:
            assert(insn.rd is not None)
            assert(insn.rt is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rt) + insn.imm
            ret_byte = self.data_mem.read_byte(addr)

            if insn.name == InsnName.LB:
                # signed extension
                se_word = BitArray(int=ret_byte.int, length=32)
            else:  # LBU
                # unsigned extension
                se_word = BitArray(uint=ret_byte.uint, length=32)

            self.write_gpr(insn.rd, se_word)

            self.pc += 1             # update the PC

        elif insn.name == InsnName.SW:
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rt) + insn.imm
            self.data_mem.write_word(addr, self.gprf.read(insn.rs))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.SB:
            assert(insn.rs is not None)
            assert(insn.rt is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rt) + insn.imm
            self.data_mem.write_byte(addr, self.gprf.read(insn.rs)[24:32])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.SMIS:
            assert(insn.si is not None)
            assert(insn.sq_list is not None)
            self.qotrf.set_sq_reg(insn.si, insn.sq_list)
            self.pc += 1             # update the PC

        elif insn.name == InsnName.SMIT:
            assert(insn.ti is not None)
            assert(insn.tq_list is not None)
            self.qotrf.set_tq_reg(insn.ti, insn.tq_list)
            self.pc += 1             # update the PC

        elif insn.name == InsnName.BUNDLE:
            assert(insn.op_tr_pair is not None)
            raise NotImplementedError("Bundle is not supported yet.")

        else:
            raise ValueError(
                "Found undefined instruction ({}).".format(insn))

        return True
