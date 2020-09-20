from pycactus.eqasm_lexer import Eqasm_lexer
from pycactus.global_config import pycactus_root_dir

eqasm_lexer = Eqasm_lexer()
eqasm_lexer.build(debug=True)
eqasm_dir = pycactus_root_dir / 'tests' / 'eqasm'
custom_file = eqasm_dir / 'custom.eqasm'
data = custom_file.read_text()
eqasm_lexer.test(data)
