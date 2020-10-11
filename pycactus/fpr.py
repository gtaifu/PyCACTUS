from bitstring import BitArray
import pycactus.global_config as gc
from pycactus.utils import get_logger
from .bit_array_cell import Bit_array_cell

logger = get_logger((__name__).split('.')[-1])


class Floating_point_register(Bit_array_cell):
    '''Floating point register, used to store FP values.
    '''

    def __init__(self, width=32):
        super().__init__(width)

    def float(self):
        return self.bitstring.float

    def __str__(self):
        return "{}".format(self.bitstring.float)

    def __add__(self, other):
        self.check_length(other)
        sum = self.bitstring.float + other.bitstring.float
        result = BitArray(float=sum, length=self._width)

        return result

    def __sub__(self, other):
        self.check_length(other)
        res = self.bitstring.float - other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result

    def __mul__(self, other):
        self.check_length(other)
        res = self.bitstring.float * other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result

    def __truediv__(self, other):
        self.check_length(other)
        res = self.bitstring.float / other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result


class FPRF():
    def __init__(self):
        self.regs = []
        for i in range(gc.NUM_GPR):
            self.regs.append(General_purpose_register(gc.GPR_WIDTH))

    def dump(self):
        for i, gpr in enumerate(self.regs):
            print('{:>15}'.format('r'+str(i) + ': ' + str(gpr)), end='  ')
            if i % 8 == 7:
                print('')

    def print_reg(self, rd):
        print("{}: {:>8}, uint: {:>11d}, int: {:>11d}".format(
            "r{}".format(rd), '0x' + str(
                self.regs[rd].bitstring.hex), self.regs[rd].bitstring.uint,
            self.regs[rd].bitstring.int))

    def write(self, rd: int, value: BitArray):
        '''Update the target register `rd` with the `value`.
        Args:
          - rd (int): the target register number
          - value (BitArray): the value to write
        '''
        logger.debug("Updating register r{} with value {}.".format(rd, value))
        self.regs[rd].update_value(value)

    def __getitem__(self, rs: int):
        return self.regs[rs]

    def read(self, rs: int):
        '''Return the bitstring stored in the register `rs`
        Args:
          - rs (int): the number of the register to read
        Ret: The bitstring (BitArray) stored in this register.
        '''
        return self.regs[rs].bitstring

    def read_signed(self, rs: int):
        return self.regs[rs].signed_value()

    def read_unsigned(self, rs: int):
        return self.regs[rs].unsigned_value()
