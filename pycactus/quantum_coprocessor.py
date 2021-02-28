from .qubit_state_sim.quantumsim import Quantumsim
from .qcp import Quantum_control_processor
from .eqasm_parser import Eqasm_parser
import logging
from .utils import get_logger, update_log_file

logger = get_logger((__name__).split('.')[-1])


class Quantum_coprocessor():
    def __init__(self, num_available_qubits=7, log_level=logging.WARNING):
        """
        Top module of the python-version cactus.
        """
        self.qubit_sim = Quantumsim(num_available_qubits)
        self.qcp = Quantum_control_processor(
            self.qubit_sim, num_available_qubits)
        self.eqasm_parser = Eqasm_parser()
        self.set_log_level(log_level)

    def set_num_available_qubits(self, num_available_qubits):

        self.qcp.set_num_available_qubits(num_available_qubits)
        self.qubit_sim.__init__(num_available_qubits)

    def set_log_level(self, log_level):
        logger.setLevel(log_level)
        self.qcp.set_log_level(log_level)
        self.qubit_sim.set_log_level(log_level)

    def set_max_exec_cycle(self, num_cycle: int):
        self.qcp.set_max_exec_cycle(num_cycle)

    def upload_program(self, prog_fn, num_available_qubits=7):
        '''Parse the eQASM assembly file and upload it to the instruction memory of the QCP.
        Args:
        - `prog_fn` (str/Path): the eQASM file to upload

        Return:
        - `True` when everything goes on successfully, otherwise `False`.
        '''
        success, insns = self.eqasm_parser.parse(filename=prog_fn, debug=True)
        if not success:
            print("Errors in the eqasm file {} and stopping program"
                  " uploading. Exit.".format(prog_fn))
            return False

        self.set_num_available_qubits(num_available_qubits)
        return self.qcp.upload_program(insns)

    def execute(self):
        '''Return True when executes successfully.
        '''
        update_log_file()
        return self.qcp.run()

    def read_result(self):
        return self.qcp.get_data_mem()
