from bitstring import BitArray
from pycactus.qcp import Quantum_control_processor
from pycactus.insn import *
import pycactus.global_config as gc


qcp = Quantum_control_processor()
for i in range(gc.NUM_GPR):
    qcp.write_gpr_value(i, int=i)


def add_insn(name, **kwargs):
    qcp.append_insn(Instruction(name=name, **kwargs))


def test_arith():
    add_insn(eqasm_insn.ADD, rd=3, rs=1, rt=2)
    add_insn(eqasm_insn.ADD, rd=4, rs=2, rt=3)
    add_insn(eqasm_insn.ADD, rd=5, rs=6, rt=2)
    add_insn(eqasm_insn.SUB, rd=10, rs=11, rt=12)
    add_insn(eqasm_insn.AND, rd=11, rs=12, rt=5)
    add_insn(eqasm_insn.OR, rd=11, rs=12, rt=5)
    add_insn(eqasm_insn.XOR, rd=11, rs=12, rt=5)
    add_insn(eqasm_insn.STOP)


def test_LDI():
    rd = 1
    large_number = 0xFF115577
    upper15bits = (large_number & 0xfffe0000) >> 17
    lower17bits = large_number & 0x1ffff
    add_insn(eqasm_insn.LDI, rd=rd, imm=lower17bits)
    qcp.advance_one_cycle()
    add_insn(eqasm_insn.LDUI, rd=rd, rs=rd, imm=upper15bits)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_int(rd) == lower17bits)
    add_insn(eqasm_insn.STOP)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_uint(rd) == large_number)


def test_CMP():

    value_pairs = [[0, 0], [1, 0], [0, 1],
                   [2**31-1, -2**31], [-2**31, 2**31-1]]

    for vp in value_pairs:
        qcp.write_gpr_value(1, int=vp[0])
        qcp.write_gpr_value(2, int=vp[1])
        add_insn(eqasm_insn.CMP, rs=1, rt=2)
        qcp.advance_one_cycle()
        qcp.print_gpr(1)
        qcp.print_gpr(2)
        qcp.dump_cmp_flags()


def test_FBR():
    qcp.write_gpr_value(1, int=0)
    qcp.write_gpr_value(2, int=1)
    add_insn(eqasm_insn.CMP, rs=1, rt=2)
    qcp.advance_one_cycle()
    qcp.dump_cmp_flags()
    for key in CMP_FLAG:
        add_insn(eqasm_insn.FBR, cmp_flag=key, rd=0)
        qcp.advance_one_cycle()
        qcp.print_gpr(0)


def test_NOT():
    qcp.write_gpr_value(1, uint=0xf0f0)
    add_insn(eqasm_insn.NOT, rt=1, rd=0)
    qcp.advance_one_cycle()
    assert(qcp.gprf.read(0) == BitArray('0xFFFF0F0F'))


def test_BR():
    add_insn(eqasm_insn.ADD, rd=3, rs=1, rt=2, labels=['start'])
    add_insn(eqasm_insn.ADD, rd=4, rs=2, rt=3)
    add_insn(eqasm_insn.ADD, rd=5, rs=6, rt=2)
    add_insn(eqasm_insn.SUB, rd=10, rs=11, rt=12)
    add_insn(eqasm_insn.AND, rd=11, rs=12, rt=5)
    add_insn(eqasm_insn.OR, rd=11, rs=12, rt=5)
    add_insn(eqasm_insn.BR, cmp_flag='ALWAYS', target_label='start')
    for i in range(30):
        qcp.advance_one_cycle()


def test_FMR():
    for i in range(len(qcp.msmt_result)):
        qcp.msmt_result[i] = i % 2

    for i in range(gc.NUM_QUBIT):
        add_insn(eqasm_insn.FMR, rd=0, qs=i)
        qcp.advance_one_cycle()
        assert(qcp.read_gpr_int(0) == (i % 2))


def test_ADD():
    qcp.print_gpr(0)
    qcp.write_gpr_value(1, int=2**31-1)
    qcp.write_gpr_value(2, int=2**31-1)
    qcp.write_gpr_value(3, int=-2**31)
    qcp.write_gpr_value(4, int=-2**31)

    add_insn(eqasm_insn.ADD, rd=0, rs=1, rt=2)
    add_insn(eqasm_insn.ADD, rd=5, rs=3, rt=4)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_int(0) == -2)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_int(5) == 0)


def test_SUB():
    add_insn(eqasm_insn.SUB, rd=10, rs=11, rt=12)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_int(10) == -1)


def test_LW_SW():
    qcp.write_gpr_value(2, uint=100)
    qcp.write_gpr_value(0, uint=0)
    qcp.write_gpr_value(1, uint=0)
    add_insn(eqasm_insn.SW, rs=2, imm=0, rt=0)
    add_insn(eqasm_insn.LW, rd=1, imm=0, rt=0)
    qcp.advance_one_cycle()
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_uint(1) == 100)


def test_sb_lb():
    qcp.write_gpr_value(0, uint=0)
    qcp.write_gpr_value(1, uint=1)
    qcp.write_gpr_value(2, uint=0xF1)
    add_insn(eqasm_insn.SB, rs=2, imm=10, rt=0)
    add_insn(eqasm_insn.SB, rs=2, imm=11, rt=0)
    add_insn(eqasm_insn.SB, rs=2, imm=12, rt=0)
    qcp.advance_one_cycle()
    qcp.advance_one_cycle()
    qcp.advance_one_cycle()
    add_insn(eqasm_insn.LW, rd=1, imm=10, rt=0)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_int(1) == 0xf1f1f1)
    add_insn(eqasm_insn.LB, rd=1, imm=10, rt=0)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_uint(1) == 0xfffffff1)
    add_insn(eqasm_insn.LBU, rd=1, imm=10, rt=0)
    qcp.advance_one_cycle()
    assert(qcp.read_gpr_uint(1) == 0x000000f1)


test_CMP()
