from pycactus.fpr import FPRF
from bitstring import BitArray
from .utils import *
from .qotr import QOTRF
from .insn import *
from .gpr import *
from .memory import Memory
import pycactus.global_config as gc
from .qubit_state_sim.if_qubit_sim import If_qubit_sim

logger = get_logger((__name__).split('.')[-1])
logger.setLevel(logging.DEBUG)


class Quantum_control_processor():
    def __init__(self, qubit_state_sim, start_addr=0):
        # assert(isinstance(qubit_state_sim, If_qubit_sim))

        self.qubit_state_sim = qubit_state_sim

        # general purpose register file
        self.gprf = GPRF(num_gpr=gc.NUM_GPR, gpr_width=gc.GPR_WIDTH)
        # floating point register file
        self.fprf = FPRF(num_fpr=gc.NUM_FPR, fpr_width=gc.FPR_WIDTH)

        # operation target register files
        self.qotrf = QOTRF()

        # measurement result register
        self.msmt_result = [0] * gc.NUM_QUBIT

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
        '''Update the target GPR `rd` with the `value`.
        Args:
        - `rd` (int): the GPR number in the GPR file.
        - `value` (BitArray): the value to write.

        Note: the value should be converted into the BitArray format.
        '''
        if isinstance(value, int):
            value = BitArray(int=value, length=32)
        self.gprf.write(rd, value)

    def write_fpr(self, fd: int, value: BitArray):
        '''Update the target FP register `fd` with the `value`
        Args:
        - `rd` (int): the GPR number in the GPR file.
        - `value` (BitArray): the value to write.

        Note: the floating point value should be converted into the BitArray format.
        '''
        if isinstance(value, int):
            value = BitArray(int=value, length=32)
        self.fprf.write(fd, value)

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

        # ------------------------- FP operations -------------------------
        elif insn.name == InsnName.FCVT_S_W:
            # Convert the 32-bit FP number stored in fs into a 32-bit
            # integer and store it in rd.
            assert(insn.rd is not None)
            assert(insn.fs is not None)

            float_value = self.fprf[insn.fs].float()
            self.write_gpr(insn.rd, BitArray(
                int=int(float_value), length=len(self.gprf[insn.rd])))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FCVT_W_S:
            # Convert the 32-bit signed integer in rs to a 32-bit FP number,
            # and store it in fd.
            assert(insn.fd is not None)
            assert(insn.rs is not None)

            int_value = self.read_gpr_signed(insn.rs)
            self.write_fpr(insn.fd, BitArray(
                float=int_value, length=len(self.fprf[insn.fd])))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FSW:
            assert(insn.fs is not None)
            assert(insn.rr is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rs) + insn.imm
            self.data_mem.write_word(addr, self.fprf.read(insn.fs))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FLW:
            assert(insn.fd is not None)
            assert(insn.rs is not None)
            assert(insn.imm is not None)

            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_unsigned(insn.rs) + insn.imm
            ret_word = self.data_mem.read_word(addr)
            self.write_fpr(insn.fd, ret_word)

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FADD_S:
            assert(insn.fd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            self.write_fpr(insn.fd, self.fprf[insn.fs] + self.fprf[insn.ft])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FSUB_S:
            assert(insn.fd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            self.write_fpr(insn.fd, self.fprf[insn.fs] - self.fprf[insn.ft])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FMUL_S:
            assert(insn.fd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            self.write_fpr(insn.fd, self.fprf[insn.fs] * self.fprf[insn.ft])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FDIV_S:
            assert(insn.fd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            self.write_fpr(insn.fd, self.fprf[insn.fs] / self.fprf[insn.ft])

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FEQ_S:
            assert(insn.rd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            res = int(self.fprf[insn.fs].float() == self.fprf[insn.ft].float())
            self.write_gpr(insn.rd, BitArray(
                int=res, length=self.gprf[insn.rd]))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FLT_S:
            assert(insn.rd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            res = int(self.fprf[insn.fs].float() < self.fprf[insn.ft].float())
            self.write_gpr(insn.rd, BitArray(
                int=res, length=self.gprf[insn.rd]))

            self.pc += 1             # update the PC

        elif insn.name == InsnName.FLE_S:
            assert(insn.rd is not None)
            assert(insn.fs is not None)
            assert(insn.ft is not None)
            res = int(self.fprf[insn.fs].float() <= self.fprf[insn.ft].float())
            self.write_gpr(insn.rd, BitArray(
                int=res, length=self.gprf[insn.rd]))

            self.pc += 1             # update the PC

        # ------------------------- quantum operation -------------------------
        elif insn.name == InsnName.BUNDLE:
            assert(insn.q_ops is not None)
            for qop in insn.q_ops:
                op_name = qop.name

                if qop.sreg is not None:
                    target_qubit_list = self.qotrf.read_sq_reg(qop.sreg)

                    logger.info(
                        "single-qubit operation: {} {}".format(op_name, target_qubit_list))

                    for qubit in target_qubit_list:
                        if op_name.lower() in ['measure', 'measz']:
                            self.msmt_result[qubit] = self.qubit_state_sim.measure_qubit(
                                qubit)
                        else:
                            self.qubit_state_sim.apply_single_qubit_gate(
                                op_name, qubit)

                elif qop.treg is not None:
                    # currently only support CZ operation
                    assert(op_name.lower() == 'cz')
                    target_qubit_pairs = self.qotrf.read_tq_reg(qop.treg)

                    logger.info(
                        "two-qubit operation: CZ {}".format(target_qubit_pairs))

                    for pair in target_qubit_pairs:
                        self.qubit_state_sim.apply_two_qubit_gate(
                            pair[0], pair[1])

            self.pc += 1

        else:
            raise ValueError(
                "Found undefined instruction ({}).".format(insn))

        return True
