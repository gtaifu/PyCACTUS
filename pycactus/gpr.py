from bitstring import BitArray
import pycactus.global_config as gc
from pycactus.utils import get_logger

logger = get_logger((__name__).split('.')[-1])


class General_purpose_register():
    '''General purpose register, used to store integers.
    '''

    def __init__(self, width):
        assert(isinstance(width, int))
        # the width is supposed not to change in the future
        self.bitstring = BitArray(width)
        self._width = width

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


class GPRF():
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
