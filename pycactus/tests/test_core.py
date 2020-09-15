from pycactus.middle_end.core import General_purpose_register, InsnName, InsnType, Instruction, Quantum_control_processor
from pycactus.middle_end import *

gpr0 = General_purpose_register(32)
gpr1 = General_purpose_register(32)
gpr2 = General_purpose_register(32)

gpr0.update_value(10)
gpr1.update_value(100)
gpr2.update_value(gpr0 + gpr1)

print(gpr0)
print(gpr1)
print(gpr2)

qcp = Quantum_control_processor()

for i in range(len(qcp.gprf)):
    qcp.gprf[i].update_value(i)


stop_insn = Instruction(name=InsnName.STOP)

qcp.append_insn(Instruction(name=InsnName.ADD, rd=3, rs=1, rt=2))
qcp.append_insn(Instruction(name=InsnName.ADD, rd=4, rs=2, rt=3))
qcp.append_insn(Instruction(name=InsnName.ADD, rd=5, rs=6, rt=2))
qcp.append_insn(Instruction(name=InsnName.SUB, rd=10, rs=11, rt=12))
qcp.append_insn(Instruction(name=InsnName.AND, rd=11, rs=12, rt=5))
qcp.append_insn(Instruction(name=InsnName.OR, rd=11, rs=12, rt=5))
qcp.append_insn(Instruction(name=InsnName.XOR, rd=11, rs=12, rt=5))
qcp.append_insn(stop_insn)

qcp.run()
