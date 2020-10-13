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

    def signed_value(self):
        return self.bitstring.int

    def unsigned_value(self):
        return self.bitstring.uint

    def __str__(self):
        return "{}".format(self.bitstring.int)

    def __len__(self):
        return self._width

    def check_length(self, other):
        if self.__len__() != len(other):
            raise ValueError("Cannot perform addition on two bitstring with different"
                             " length ({}, {})".format(self.__len__(), len(other)))

    def __add__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint + other.bitstring.uint
        # omit the carry-in bit
        result = BitArray(uint=unsigned_sum,
                          length=self._width+1)[1:self._width+1]

        return result

    def __invert__(self):
        return ~self.bitstring

    def __sub__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint + (~other.bitstring).uint + 1

        # omit the carry-in bit
        result = BitArray(uint=unsigned_sum,
                          length=self._width+1)[1:self._width+1]

        return result

    def __and__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint & other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __or__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint | other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def __xor__(self, other):
        self.check_length(other)
        unsigned_sum = self.bitstring.uint ^ other.bitstring.uint
        return BitArray(uint=unsigned_sum, length=self._width)

    def truediv(self, other):
        self.check_length(other)
        div_res = self.bitstring.int / other.bitstring.int
        return BitArray(int=div_res, length=self._width)

    def __mul__(self, other):
        self.check_length(other)
        mul_res = self.bitstring.int * other.bitstring.int
        return BitArray(int=mul_res, length=self._width)

    def __mod__(self, other):
        self.check_length(other)
        mul_res = self.bitstring.int % other.bitstring.int
        return BitArray(int=mul_res, length=self._width)

    def __eq__(self, other):
        self.check_length(other)
        return self.bitstring == other.bitstring

    def __ne__(self, other):
        self.check_length(other)
        return self.bitstring != other.bitstring

    def __getitem__(self, item):
        return self.bitstring[item]

    def update_value(self, value: BitArray):
        '''Update the value of this register to `value`.
        Args:
          - value (BitArray): the value to write
        '''

        if self._width != len(value):
            raise ValueError("Given value has a bitstring with a different length ({}) "
                             " to the original length ({})".format(len(value), self._width))

        self.bitstring = value


class GPRF(Register_file):
    def __init__(self, num_gpr=32, gpr_width=32):
        super().__init__(General_purpose_register, num_reg=num_gpr, reg_width=gpr_width)

    def print_reg(self, rd):
        print("{}: {:>8}, uint: {:>11d}, int: {:>11d}".format(
            "r{}".format(rd), '0x' + str(
                self.regs[rd].bitstring.hex), self.regs[rd].bitstring.uint,
            self.regs[rd].bitstring.int))

    def read_signed(self, rs: int):
        return self.regs[rs].signed_value()

    def read_unsigned(self, rs: int):
        return self.regs[rs].unsigned_value()
