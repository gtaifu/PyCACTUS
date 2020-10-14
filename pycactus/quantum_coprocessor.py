
from .eqasm_parser import Eqasm_parser
from .qcp import Quantum_control_processor
from .qubit_state_sim.quantumsim import Quantumsim
from .global_config import NUM_QUBIT


class Quantum_coprocessor():
    def __init__(self):
        """
        Top module of the python-version cactus.
        """
        self.qubit_sim = Quantumsim(NUM_QUBIT)
        self.qcp = Quantum_control_processor(self.qubit_sim)
        self.eqasm_parser = Eqasm_parser()

    def upload_program(self, prog_fn):
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

        return self.qcp.upload_program(insns)

    def execute(self):
        '''Return True when executes successfully.
        '''
        return self.qcp.run()

    def read_result(self):
        return self.qcp.get_data_mem()
