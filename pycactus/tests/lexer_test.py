from pycactus.eqasm_lexer import Eqasm_lexer
from pycactus.global_config import pycactus_root_dir
from pathlib import Path

eqasm_lexer = Eqasm_lexer()
eqasm_lexer.build(debug=True)
eqasm_dir = pycactus_root_dir / 'tests' / 'eqasm'
# custom_file = eqasm_dir / 'custom.eqasm'
# custom_file = eqasm_dir / 'test_string.eqasm'
custom_file = Path(r'D:\GitHub\git_pcl\test_examples\syntax\expressions\Add\build\test_add.eqasm')
data = custom_file.read_text()
# test_qisa = eqasm_dir / 'test_assembly.qisa'
# data = test_qisa.read_text()
eqasm_lexer.test(data)
