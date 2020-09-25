from pycactus.eqasm_parser import Eqasm_parser

eqasm_parser = Eqasm_parser()

# r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\custom.eqasm'
fn = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'
for insn in eqasm_parser.parse(filename=fn, debug=True):
    print(insn)
