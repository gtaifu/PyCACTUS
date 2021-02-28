import logging
from pycactus.quantum_coprocessor import Quantum_coprocessor
from pathlib import Path


cur_dir = Path(__file__).absolute().parent
eqasm_dir = cur_dir / 'eqasm'

sim = Quantum_coprocessor(log_level=logging.DEBUG)
sim.set_max_exec_cycle(1000000)
pf = eqasm_dir / 'test_add.eqasm'
# pf = r'D:\GitHub\git_pcl\test_examples\syntax\expressions\Array\access\build\dynamic_write.eqasm'

sim.upload_program(pf)

sim.execute()
