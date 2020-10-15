from .quantumsim_wrapper import interface_quantumsim
from .if_qubit_sim import If_qubit_sim
from pycactus.utils import get_logger
import logging

logger = get_logger((__name__).split('.')[-1])


class Quantumsim(If_qubit_sim):
    def __init__(self, num_qubit: int):
        """
        Interface for the qubit state simulator .
        """
        super().__init__('quantumsim')

        self.quantumsim = interface_quantumsim()
        self.quantumsim.init_dm(num_qubit)
        self.quantumsim.print_classical_state()
        logger.info("initialize quantumsim")

    def apply_quantum_operation(self):
        pass

    def apply_idle_gate(self, idle_duration, qubit):
        self.quantumsim.calculate_gamma_lamda(idle_duration)
        self.quantumsim.prepare_idling_ptm()
        self.quantumsim.apply_ptm()

    def apply_single_qubit_gate(self, operation, qubit):
        logger.info("apply operation {} on qubit {}".format(operation, qubit))
        if operation.lower() == 'null':
            return
        self.quantumsim.prepare_ptm(operation)
        self.quantumsim.apply_ptm(qubit)

    def apply_two_qubit_gate(self, qubit0, qubit1):
        logger.info("apply CZ on qubit pair ({}, {})".format(qubit0, qubit1))
        self.quantumsim.prepare_two_ptm()
        self.quantumsim.apply_two_ptm(qubit0, qubit1)

    def measure_qubit(self, qubit):
        logger.info("measure qubit: {}".format(qubit))
        self.quantumsim.prepare_idling_ptm()
        self.quantumsim.apply_ptm(qubit)
        self.quantumsim.apply_measurement(qubit)
        msmt_result = self.quantumsim.return_measurement_result()
        print("measurement qubit {}, get result: {}.".format(qubit, msmt_result))
        return msmt_result
