from pathlib import Path
from pycactus.eqasm_parser import Eqasm_parser

eqasm_parser = Eqasm_parser()


cur_dir = Path(__file__).absolute().parent
eqasm_dir = cur_dir / 'eqasm'

fn = eqasm_dir / 'bellstate_loop.eqasm'
fn = eqasm_dir / 'fp.eqasm'
fn = eqasm_dir / 'test_assembly.qisa'
fn = eqasm_dir / 'custom.eqasm'

success, insns = eqasm_parser.parse(filename=fn, debug=True)
if not success:
    print("Errors in the eqasm file {} and stopping program"
          " uploading.".format(fn))
    exit(-1)

out_fn = Path(fn).parent / 'bouncing_backout.eqasm'
with out_fn.open('w') as f:
    for insn in insns:
        # print(insn)
        f.write("{}\n".format(insn))
