
def test_gpr():
    gpr0 = General_purpose_register(32)
    gpr1 = General_purpose_register(32)
    gpr2 = General_purpose_register(32)

    gpr0.update_value(10)
    gpr1.update_value(100)
    gpr2.update_value(gpr0 + gpr1)

    assert(str(gpr0) == '10')
    assert(str(gpr1) == '100')
    assert(str(gpr2) == '110')