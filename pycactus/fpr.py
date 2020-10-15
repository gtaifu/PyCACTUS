from bitstring import BitArray
import pycactus.global_config as gc
from pycactus.utils import get_logger
from .bit_array_cell import Bit_array_cell, Register_file

logger = get_logger((__name__).split('.')[-1])


class Floating_point_register(Bit_array_cell):
    '''Floating point register, used to store FP values.
    '''

    def __init__(self, width=32):
        super().__init__(width)

    @classmethod
    def reg_symbol(cls):
        return 'f'

    def float(self):
        return self.bitstring.float

    def __str__(self):
        print("print floating value")
        return "{}".format(self.bitstring.float)

    def __add__(self, other):
        # self.check_length(other)
        sum = self.bitstring.float + other.bitstring.float
        result = BitArray(float=sum, length=self._width)

        return result

    def __sub__(self, other):
        # self.check_length(other)
        res = self.bitstring.float - other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result

    def __mul__(self, other):
        # self.check_length(other)
        res = self.bitstring.float * other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result

    def __truediv__(self, other):
        # self.check_length(other)
        res = self.bitstring.float / other.bitstring.float
        result = BitArray(float=res, length=self._width)

        return result


class FPRF(Register_file):
    def __init__(self, num_fpr=32, fpr_width=32):
        super().__init__(Floating_point_register, num_reg=num_fpr, reg_width=fpr_width)

    def read_float(self, fs: int):
        return self.regs[fs].float()
