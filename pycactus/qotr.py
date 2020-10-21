import pycactus.global_config as gc


class QOTRF():
    def __init__(self, max_qubit_num=7):
        self.max_qubit_num = max_qubit_num
        self.sq_regs = [None] * gc.NUM_SQ_QOTR
        self.tq_regs = [None] * gc.NUM_TQ_QOTR

    def set_num_available_qubits(self, max_qubit_num):
        print('QOTRF max_qubit_num: {}'.format(max_qubit_num))
        self.max_qubit_num = max_qubit_num

    def set_sq_reg(self, si, qubit_list):
        assert(isinstance(qubit_list, list) and len(qubit_list) > 0)

        if not all([qubit < self.max_qubit_num for qubit in qubit_list]):
            raise ValueError("Given qubit list ({}) contains "
                             "invalid qubit numbers.".format(qubit_list))

        self.sq_regs[si] = qubit_list

    def read_sq_reg(self, si):
        return self.sq_regs[si]

    def set_tq_reg(self, ti, qubit_pair_list):
        assert(isinstance(qubit_pair_list, list) and len(qubit_pair_list) > 0)

        if not all([(qp[0] < self.max_qubit_num and qp[1] < self.max_qubit_num)
                    for qp in qubit_pair_list]):
            raise ValueError("Given qubit list ({}) contains "
                             "invalid qubit numbers.".format(qubit_pair_list))

        self.tq_regs[ti] = qubit_pair_list

    def read_tq_reg(self, ti):
        return self.tq_regs[ti]
