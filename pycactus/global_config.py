from pathlib import Path

pycactus_root_dir = Path(__file__).absolute().parent

SIZE_INSN_MEM = int(1e6)  # accept up to 1 million instructions.
MEM_ADDR_WIDTH = 22
SIZE_DATA_MEM = 2 ** MEM_ADDR_WIDTH  # 4 MiB for now
NUM_GPR = 32
GPR_WIDTH = 32

# number of FP registers
NUM_FPR = 32

# number of single-qubit operation target registers
NUM_SQ_QOTR = 32
# number of two-qubit operation target registers
NUM_TQ_QOTR = 64

NUM_QUBIT = 7
