import pycactus.global_config as gc


# class Sq_register():
#     def __init__(self, max_num_qubit):
#         self._max_num_qubit = max_num_qubit
#         self._target_qubits = []

#     def __getitem__(self, item):
#         """Return indexed operation."""
#         return self._target_qubits[item]

#     def __len__(self):
#         """Return number of qubit pairs in this single-qubit target register."""
#         return len(self._target_qubits)

#     def append(self, qubit):
#         assert(isinstance(qubit, int))

#         if qubit not in self._target_qubits:
#             if self.__len__() >= self.max_num_qubit:
#                 raise ValueError("The sq_register is already full (with {} elements).".format(
#                     self.max_num_qubit))
#             else:
#                 self._target_qubits.append(qubit)


# class Tq_register():
#     def __init__(self, max_num_qubit_pair: int):
#         self._qubit_pairs = []
#         self._max_num_qubit_pair = max_num_qubit_pair

#     def __getitem__(self, item):
#         """Return indexed operation."""
#         return self._qubit_pairs[item]

#     def __len__(self):
#         """Return number of qubit pairs in this two-qubit target register."""
#         return len(self._qubit_pairs)

#     def append(self, qubit_pair):
#         assert(isinstance(qubit_pair, tuple))
#         assert(len(qubit_pair) == 2)

#         if qubit_pair not in self._qubit_pairs:
#             if self.__len__() >= self._max_num_qubit_pair:
#                 raise ValueError("The tq_register is already full (with {} elements).".format(
#                     self._max_num_qubit_pair))
#             else:
#                 self._qubit_pairs.append(qubit_pair)

#     # def __iadd__(self, qubit_pair):
#     #     """Overload += to implement self.extend."""
#     #     return self.append(qubit_pair)


class QOTRF():
    def __init__(self):
        self.sq_regs = [None] * gc.NUM_SQ_QOTR
        # for i in range(gc.NUM_SQ_QOTR):
        #     self.sq_regs.append(Sq_register(gc.NUM_QUBIT))

        self.tq_regs = [None] * gc.NUM_TQ_QOTR
        # for i in range(gc.NUM_SQ_QOTR):
        #     self.sq_regs.append(Sq_register(gc.NUM_QUBIT))

    def set_sq_reg(self, si, qubit_list):
        assert(isinstance(qubit_list, list) and len(qubit_list) > 0)

        if not all([qubit < gc.NUM_QUBIT for qubit in qubit_list]):
            raise ValueError("Given qubit list ({}) contains "
                             "invalid qubit numbers.".format(qubit_list))

        self.sq_regs[si] = qubit_list

    def read_sq_reg(self, si):
        return self.sq_regs[si]

    def set_tq_reg(self, ti, qubit_pair_list):
        assert(isinstance(qubit_pair_list, list) and len(qubit_pair_list) > 0)

        if not all([(qp[0] < gc.NUM_QUBIT and qp[1] < gc.NUM_QUBIT)
                    for qp in qubit_pair_list]):
            raise ValueError("Given qubit list ({}) contains "
                             "invalid qubit numbers.".format(qubit_pair_list))

        self.tq_regs[ti] = qubit_pair_list

    def read_tq_reg(self, ti):
        return self.tq_regs[ti]
