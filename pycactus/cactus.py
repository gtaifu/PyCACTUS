
from .eqasm_parser import Eqasm_parser
from .qcp import Quantum_control_processor
from qgrtsys.if_backend.if_backend import If_backend


class Py_cactus(If_backend):
    def __init__(self):
        """
        Top module of the python-version cactus.
        """
        self.qcp = Quantum_control_processor()

        # can we remove this file name?
        self.eqasm_parser = Eqasm_parser()

    def upload_program(self, prog_fn):
        success, insns = self.eqasm_parser.parse(filename=prog_fn, debug=True)
        if not success:
            print("Errors in the eqasm file {} and stopping program"
                  " uploading.".format(prog_fn))
            exit(-1)

        self.qcp.upload_program(insns)

    def execute(self):
        self.qcp.run()
