from pycactus.cactus import Py_cactus

sim = Py_cactus()
pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\bellstate_loop.eqasm'
# pf = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'

sim.upload_program(pf)

sim.execute()
