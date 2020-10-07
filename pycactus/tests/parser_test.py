from pathlib import Path
from pycactus.eqasm_parser import Eqasm_parser

eqasm_parser = Eqasm_parser()

# r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\custom.eqasm'
# fn = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\test_assembly.qisa'
fn = r'D:\GitHub\git_pcl\PyCACTUS\pycactus\tests\eqasm\bellstate_loop.eqasm'
success, insns = eqasm_parser.parse(filename=fn, debug=True)
if not success:
    print("Errors in the eqasm file {} and stopping program"
          " uploading.".format(fn))
    exit(-1)

# for l in label_addr:
#     insns[label_addr[l]].labels.append(l)

out_fn = Path(fn).parent / 'bouncing_backout.eqasm'
with out_fn.open('w') as f:
    for insn in insns:
        # print(insn)
        f.write("{}\n".format(insn))
