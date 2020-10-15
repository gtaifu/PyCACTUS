class If_qubit_sim:
    def __init__(self, name):
        """
        Interface used by pycactus to call a qubit state simulator.

        Any actual python-based qubit simulator that aims to connect to CACTUS should
        be wrapped by a class inherited from this class.
        """
        self.name = name

    def apply_single_qubit_gate(self, operation, qubit):
        raise NotImplementedError

    def apply_two_qubit_gate(self, qubit0, qubit1):
        raise NotImplementedError

    def measure_qubit(self, qubit):
        raise NotImplementedError
