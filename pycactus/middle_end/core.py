
class Sq_register:
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


class Tq_register:
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


class General_purpose_register:
    def __init__(self):
        self._width = 32


class Quantum_control_processor:
    def __init__(self):
        self.gprf = None
        self.fprf = None
        # single-qubit operation target register file
        self.sqotrf = Sq_register(32)
        # two-qubit operation target register file
        self.tqotrf = Tq_register(32)

        self.program_fn = None
