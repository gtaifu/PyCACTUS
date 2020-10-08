from pycactus.quantum_coprocessor import Quantum_coprocessor
from pathlib import Path

cur_dir = Path(__file__).absolute().parent
eqasm_dir = cur_dir / 'eqasm'

sim = Quantum_coprocessor()

pf = eqasm_dir / 'bellstate_loop.eqasm'
pf = eqasm_dir / 'test_add.eqasm'
pf = eqasm_dir / 'bundle_test.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\bellstate_loop.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'

sim.upload_program(pf)

sim.execute()
