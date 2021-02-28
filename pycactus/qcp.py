from pycactus.fpr import FPRF
from bitstring import BitArray
from .utils import *
from .qotr import QOTRF
from .insn import *
from .gpr import *
from .memory import Memory
import pycactus.global_config as gc

logger = get_logger((__name__).split('.')[-1])


class Quantum_control_processor():
    def __init__(self, qubit_state_sim=None, num_available_qubits=7,
                 start_addr=0, log_level=logging.WARNING,
                 max_exec_cycle=5000000):
        self.qubit_state_sim = qubit_state_sim

        # general purpose register file
        self.gprf = GPRF(num_gpr=gc.NUM_GPR, gpr_width=gc.GPR_WIDTH)
        # floating point register file
        self.fprf = FPRF(num_fpr=gc.NUM_FPR, fpr_width=gc.FPR_WIDTH)

        # operation target register files
        self.qotrf = QOTRF()

        self.max_insn_num = gc.SIZE_INSN_MEM
        self.start_addr = start_addr

        # data memory
        self.data_mem = Memory(size=gc.SIZE_DATA_MEM, parent_qcp=self)
        self.set_num_available_qubits(num_available_qubits)
        self.max_exec_cycle = max_exec_cycle

        self.reset()
        self.set_log_level(log_level)
        # self.exec_trace_fn = 'exec_trace.csv'
        # try:
        #     self.trace_f = open(self.exec_trace_fn, 'w')
        # except:
        #     raise OSError("QCP: Cannot open the trace file: {}".format(self.exec_trace_fn))

    def set_num_available_qubits(self, num_available_qubits):
        self._num_available_qubits = num_available_qubits
        self.qotrf.set_num_available_qubits(num_available_qubits)
        # measurement result register
        self.msmt_result = [0] * num_available_qubits

    def set_log_level(self, log_level):
        logger.setLevel(log_level)
        self.data_mem.set_log_level(log_level)
        self.gprf.set_log_level(log_level)

    def set_max_exec_cycle(self, num_cycle: int):
        self.max_exec_cycle = num_cycle

    def get_data_mem(self):
        return self.data_mem.get_entire_mem()

    def reset(self):
        '''Completely reset the QCP state. Except the data memory, all memory is cleaned.
        Should be used before uploading a new program.

        N.B.: we do not need to reset the data memory during the reset process.
        '''
        self.restart()
        # instruction memory
        self.insn_mem = []
        self.label_addr = {}
        # self.data_mem = Memory(size=gc.SIZE_DATA_MEM, parent_qcp=self)

    def restart(self):
        '''Restart the program. All architectural states except the instruction memory
        and data memory are reset to the initial state.
        Should be used when restarting the same program.
        '''
        self.stop_bit = 0
        self.cycle = 0
        self.pc = self.start_addr
        # qubit measurement result
        self.msmt_result = [0] * self._num_available_qubits
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

        return True

    def parse_labels(self):
        self.label_addr = {}
        for i, insn in enumerate(self.insn_mem):
            for label in insn.labels:
                self.label_addr[label] = i

        for insn in self.insn_mem:
            if insn.name in [eqasm_insn.BR]:
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

    def write_gpr_value(self, rd: int, **kwargs):
        '''Write the target GPR `rd` with the value specified by a key-word argument.

        Args:
        - `rd` (int): the GPR number in the GPR file.
        - kwargs: the key-word argument specifying the value to write, which could be:
          + `int`
          + `uint`

        Example:
            `self.write_gpr_value(3, int=100)`
        '''

        assert(len(kwargs) == 1 and list(kwargs.keys())[0] in ['int', 'uint'])
        bit_array = BitArray(length=gc.GPR_WIDTH, **kwargs)

        self.write_gpr_bits(rd, bit_array)

    def write_gpr_bits(self, rd: int, value: BitArray):
        '''Update the target GPR `rd` with the BitArray `value`.
        Args:
        - `rd` (int): the GPR number in the GPR file.
        - `value` (BitArray): the BitArray-format value to write.
        '''
        self.gprf.write(rd, value)

    def write_fpr_value(self, fd: int, value: float):
        '''Write the target GPR `fd` with the FP `value`.

        Args:
        - `fd` (int): the GPR number in the GPR file.
        - `value`: the FP value to write.

        Example:
            `self.write_gpr_value(3, 100.0)`
        '''
        bit_array = BitArray(length=gc.FPR_WIDTH, float=value)
        self.write_fpr_bits(fd, bit_array)

    def write_fpr_bits(self, fd: int, value: BitArray):
        '''Update the target FP register `fd` with the BitArray `value`.
        Args:
        - `rd` (int): the GPR number in the GPR file.
        - `value` (BitArray): the BitArray value to write.
        '''
        self.fprf.write(fd, value)

    def read_gpr_uint(self, rs: int):
        return self.gprf.read_unsigned(rs)

    def read_gpr_int(self, rs: int):
        return self.gprf.read_signed(rs)

    def print_gpr(self, rd):
        self.gprf.print_reg(rd)

    def advance_one_cycle(self):
        self.cycle += 1

        # fetch the instruction
        insn = self.insn_mem[self.pc]

        if self.cycle > 0:
            log_msg = "cycle: {}, lineno: {}, insn: {}\n".format(
                self.cycle, insn.lineno, insn)
            logger.debug(log_msg)
            # self.trace_f.write(log_msg)

        self.process_insn(insn)  # execute

    def run(self):
        while (self.stop_bit == 0):
            self.advance_one_cycle()
            # print('\rcycle: {}, PC: {}'.format(self.cycle, self.pc), end='')
            if self.cycle > self.max_exec_cycle:
                break

        logger.info(
            "pycactus exits after executing {} cycles.".format(self.cycle))
        return True

    def process_insn(self, insn):
        # ------------------------- no operand -------------------------
        if insn.name == eqasm_insn.STOP:
            self.stop_bit = 1
            self.pc += 1             # update the PC
            self.data_mem.final_dump()

        elif insn.name == eqasm_insn.NOP:
            self.pc += 1             # update the PC

        # ---------------------------- debug ----------------------------
        elif insn.name == eqasm_insn.DUMPMEM:
            if (insn.cmp_flag.startswith('r')):
                reg_num = int(insn.cmp_flag[1:])
                print('dumping register ' + insn.cmp_flag)
                self.print_gpr(reg_num)
            elif (insn.cmp_flag == ''):
                self.data_mem.dump_content(insn.imm)
            else:
                self.data_mem.decode_data(insn.imm, insn.cmp_flag)
            self.pc += 1

        # ------------------------- one operand -------------------------
        elif insn.name == eqasm_insn.QWAIT:  # currently ignore all timing related insns.
            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.QWAITR:
            self.pc += 1             # update the PC

        # ------------------------- two operands -------------------------
        elif insn.name == eqasm_insn.NOT:
            print("~self.gprf[insn.rt]: ", ~self.gprf[insn.rt])
            self.write_gpr_bits(insn.rd, ~self.gprf[insn.rt])
            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.CMP:
            for key in ['eq', 'ne']:
                self.cmp_flags[CMP_FLAG[key]] = cmp_op[key](self.gprf[insn.rs],
                                                            self.gprf[insn.rt])

            for key in ['lt', 'ge', 'le', 'gt']:
                self.cmp_flags[CMP_FLAG[key]] = cmp_op[key](self.read_gpr_int(insn.rs),
                                                            self.read_gpr_int(insn.rt))

            for key in ['ltu', 'geu', 'leu', 'gtu']:
                self.cmp_flags[CMP_FLAG[key]] = cmp_op[key](self.read_gpr_uint(insn.rs),
                                                            self.read_gpr_uint(insn.rt))

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.BR:
            if self.cmp_flags[CMP_FLAG[insn.cmp_flag]]:
                self.pc = self.label_addr[insn.target_label]
            else:
                self.pc += 1

        elif insn.name == eqasm_insn.FBR:
            cmp_res = self.cmp_flags[CMP_FLAG[insn.cmp_flag]]
            self.write_gpr_value(insn.rd, int=cmp_res)
            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FMR:
            self.write_gpr_value(insn.rd, int=self.msmt_result[insn.qs])
            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.LDI:
            # assumed imm is already interpreted as signed integer
            self.write_gpr_value(insn.rd, int=insn.imm)

            self.pc += 1             # update the PC

        # ------------------------- three operands -------------------------
        # InsnName.ADD, InsnName.SUB, InsnName.AND, InsnName.OR, InsnName.XOR,
        # InsnName.MUL, InsnName.DIV, InsnName.REM
        elif insn.name in int_op.keys():
            res = int_op[insn.name](self.gprf[insn.rs], self.gprf[insn.rt])
            self.write_gpr_bits(insn.rd, res)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.LDUI:
            # assumed imm is already interpreted as unsigned integer
            imm15 = BitArray(uint=insn.imm, length=15)
            composed_bitstring = imm15 + self.gprf[insn.rs][15:32]

            self.write_gpr_bits(insn.rd, composed_bitstring)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.ADDI:
            self.write_gpr_value(insn.rd,
                                 int=self.read_gpr_int(insn.rs) + insn.imm)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.LW:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rt) + insn.imm
            ret_word = self.data_mem.read_word(addr)
            logger.debug('load value ({}) from the addr 0x{:x}'.format(ret_word, addr))
            self.write_gpr_bits(insn.rd, ret_word)

            self.pc += 1             # update the PC

        elif insn.name in [eqasm_insn.LB, eqasm_insn.LBU]:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rt) + insn.imm
            ret_byte = self.data_mem.read_byte(addr)

            if insn.name == eqasm_insn.LB:  # signed extension
                se_word = BitArray(int=ret_byte.int, length=32)
            else:                           # LBU, unsigned extension
                se_word = BitArray(uint=ret_byte.uint, length=32)

            self.write_gpr_bits(insn.rd, se_word)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.SW:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rt) + insn.imm
            self.data_mem.write_word(addr, self.gprf.read(insn.rs))

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.SB:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rt) + insn.imm
            self.data_mem.write_byte(addr, self.gprf.read(insn.rs)[24:32])

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.SMIS:
            self.qotrf.set_sq_reg(insn.si, insn.sq_list)
            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.SMIT:
            self.qotrf.set_tq_reg(insn.ti, insn.tq_list)
            self.pc += 1             # update the PC

        # ------------------------- FP operations -------------------------
        elif insn.name == eqasm_insn.FCVT_W_S:
            # Convert the 32-bit FP number in fs into a 32-bit signed integer,
            # and store it in rd.
            # R[rd](31:0) = integer(F[fs])
            float_value = self.fprf[insn.fs].float()

            self.write_gpr_value(insn.rd, int=int(float_value))

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FCVT_S_W:
            # Convert a 32-bit signed integer in rs into a 32-bit FP number,
            # and store it in fd.
            # F[fd] = float(R[rs](31:0))
            int_value = self.read_gpr_int(insn.rs)
            self.write_fpr_value(insn.fd, value=float(int_value))

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FMV_W_X:
            # moves the single-precision value encoded in IEEE 754-2008 standard
            #   encoding from the lower 32 bits of GPR rs to the FPR fd.
            # F[fd] = R[rs]
            # FMV.W.X fd, rs
            bitstring = self.gprf.read(insn.rs)
            self.write_fpr_bits(insn.fd, value=bitstring)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FMV_X_W:
            # FMV.X.W moves the single-precision value in floating-point register fs
            #   represented in IEEE 754-2008 encoding to the lower 32 bits of integer
            #   register rd
            # R[rd] = F[fs]
            # FMV.X.W rd, fs
            bitstring = self.fprf.read(insn.fs)
            self.write_gpr_bits(insn.rd, value=bitstring)

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FSW:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rs) + insn.imm
            self.data_mem.write_word(addr, self.fprf.read(insn.fs))

            self.pc += 1             # update the PC

        elif insn.name == eqasm_insn.FLW:
            # assumed imm is already interpreted as signed integer
            addr = self.read_gpr_uint(insn.rs) + insn.imm
            ret_word = self.data_mem.read_word(addr)
            self.write_fpr_bits(insn.fd, ret_word)

            self.pc += 1             # update the PC
        elif insn.name in fp_op.keys():
            fp_res = fp_op[insn.name](self.fprf[insn.fs], self.fprf[insn.ft])
            self.write_fpr_bits(insn.fd, fp_res)

            self.pc += 1             # update the PC

        elif insn.name in fp_cmp_op.keys():
            res = int(fp_cmp_op[insn.name](
                self.fprf[insn.fs].float(), self.fprf[insn.ft].float()))

            self.write_gpr_value(insn.rd, int=res)
            self.pc += 1             # update the PC

        # ------------------------- quantum operation -------------------------
        elif insn.name == eqasm_insn.BUNDLE:
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
