from pycactus.cactus import Py_cactus
from pathlib import Path

cur_dir = Path(__file__).absolute().parent
eqasm_dir = cur_dir / 'eqasm'

sim = Py_cactus()

pf = eqasm_dir / 'bellstate_loop.eqasm'
pf = eqasm_dir / 'test_add.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\bellstate_loop.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'

sim.upload_program(pf)

sim.execute()
