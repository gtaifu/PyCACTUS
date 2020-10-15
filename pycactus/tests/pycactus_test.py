import logging
from pycactus.quantum_coprocessor import Quantum_coprocessor
from pathlib import Path

cur_dir = Path(__file__).absolute().parent
eqasm_dir = cur_dir / 'eqasm'

sim = Quantum_coprocessor()
sim.set_log_level(logging.WARNING)
sim.set_max_exec_cycle(1000000+500)

pf = eqasm_dir / 'bellstate_loop.eqasm'
pf = eqasm_dir / 'fp.eqasm'
pf = eqasm_dir / 'bundle_test.eqasm'
pf = eqasm_dir / 'test_add.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\bellstate_loop.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'

sim.upload_program(pf)

sim.execute()
