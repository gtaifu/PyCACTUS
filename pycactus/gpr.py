from bitstring import BitArray
import pycactus.global_config as gc
from pycactus.utils import get_logger
from .bit_array_cell import Bit_array_cell, Register_file

logger = get_logger((__name__).split('.')[-1])


class General_purpose_register(Bit_array_cell):
    '''General purpose register, used to store integers.
    '''

    def __init__(self, width):
        super().__init__(width)

    @classmethod
    def reg_symbol(cls):
        return 'r'

    def __str__(self):
        return "{}".format(self.int)

    def __add__(self, other):
        self.check_length(other)
        unsigned_sum = self.uint + other.uint
        # omit the carry-in bit
        result = BitArray(uint=unsigned_sum,
                          length=self._width+1)[1:self._width+1]

        return result

    def __invert__(self):
        return ~self.bitstring

    def __sub__(self, other):
        self.check_length(other)
        unsigned_sum = self.uint + (~other.bitstring).uint + 1

        # omit the carry-in bit
        result = BitArray(uint=unsigned_sum,
                          length=self._width+1)[1:self._width+1]

        return result

    def __and__(self, other):
        self.check_length(other)
        res = self.uint & other.uint
        return BitArray(uint=res, length=self._width)

    def __or__(self, other):
        self.check_length(other)
        res = self.uint | other.uint
        return BitArray(uint=res, length=self._width)

    def __xor__(self, other):
        self.check_length(other)
        res = self.uint ^ other.uint
        return BitArray(uint=res, length=self._width)

    def truediv(self, other):
        self.check_length(other)
        div_res = self.int / other.int
        return BitArray(int=div_res, length=self._width)

    def __mul__(self, other):
        self.check_length(other)
        mul_res = self.int * other.int
        return BitArray(int=mul_res, length=self._width)

    def __mod__(self, other):
        self.check_length(other)
        mul_res = self.int % other.int
        return BitArray(int=mul_res, length=self._width)

    def __eq__(self, other):
        self.check_length(other)
        return self.bitstring == other.bitstring

    def __ne__(self, other):
        self.check_length(other)
        return self.bitstring != other.bitstring


class GPRF(Register_file):
    def __init__(self, num_gpr=32, gpr_width=32):
        super().__init__(General_purpose_register, num_reg=num_gpr, reg_width=gpr_width)

    def print_reg(self, rd):
        print("{}: {:>8}, uint: {:>11d}, int: {:>11d}".format(
            "r{}".format(rd), '0x' + str(
                self.regs[rd].bitstring.hex), self.regs[rd].uint,
            self.regs[rd].int))

    def read_signed(self, rs: int):
        return self.regs[rs].int

    def read_unsigned(self, rs: int):
        return self.regs[rs].uint
