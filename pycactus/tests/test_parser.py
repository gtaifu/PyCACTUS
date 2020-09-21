from logging import debug
from pycactus import eqasm
from pycactus.eqasm_parser import Eqasm_parser

eqasm_parser = Eqasm_parser(
    r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\custom.eqasm')

for insn in eqasm_parser.parse(debug=True):
    print(insn)
