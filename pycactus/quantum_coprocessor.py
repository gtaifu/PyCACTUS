
from .eqasm_parser import Eqasm_parser
from .qcp import Quantum_control_processor
from qgrtsys.if_backend.if_backend import If_backend
from .qubit_state_sim.quantumsim import Quantumsim
from .global_config import NUM_QUBIT


class Quantum_coprocessor(If_backend):
    def __init__(self):
        """
        Top module of the python-version cactus.
        """
        super().__init__('pycactus_quantumsim')
        self.qubit_sim = Quantumsim(NUM_QUBIT)
        self.qcp = Quantum_control_processor(self.qubit_sim)
        self.eqasm_parser = Eqasm_parser()

    def available(self):
        return True

    def upload_program(self, prog_fn):
        success, insns = self.eqasm_parser.parse(filename=prog_fn, debug=True)
        if not success:
            print("Errors in the eqasm file {} and stopping program"
                  " uploading. Exit.".format(prog_fn))
            exit(-1)

        self.qcp.upload_program(insns)

    def execute(self):
        self.qcp.run()

    def read_result(self):
        return self.qcp.get_data_mem()
