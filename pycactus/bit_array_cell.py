import logging
from bitstring import BitArray
from pycactus.utils import get_logger

logger = get_logger((__name__).split('.')[-1])
logger.setLevel(logging.WARNING)


class Bit_array_cell():
    def __init__(self, width=32):
        assert(isinstance(width, int))
        # the width is supposed not to change in the future
        self.bitstring = BitArray(width)
        self._width = width

    @classmethod
    def reg_symbol(cls):
        raise NotImplementedError

    def __len__(self):
        return self._width

    def check_length(self, other):
        if self.__len__() != len(other):
            raise ValueError("Cannot perform addition on two bitstring with different"
                             " length ({}, {})".format(self.__len__(), len(other)))

    def update_value(self, value: BitArray):
        '''Update the value of this register to `value`.
        Args:
          - `value` (BitArray): the value to write
        '''
        assert(isinstance(value, BitArray))
        if self._width != len(value):
            raise ValueError("Given value has a bitstring with a different length ({}) "
                             " to the original length ({})".format(len(value), self._width))

        self.bitstring = value

    def __getitem__(self, item):
        return self.bitstring[item]


class Register_file():
    def __init__(self, base_register_type, num_reg, reg_width):
        '''Initialize the register file.

        Args:
          - `base_register_type` : the concrete register type, which should be a class inherited from the `Bit_array_cell` class.
          - `num_reg`: number of registers in this register file.
          - `reg_width`: the number of bits in each register.
        '''

        self.regs = []
        self.reg_symbol = base_register_type.reg_symbol()
        for i in range(num_reg):
            self.regs.append(base_register_type(reg_width))

    def dump(self):
        'Dump the content of the entire register file.'
        for i, reg in enumerate(self.regs):
            print('{:>15}'.format(self.reg_symbol + str(i) + ': ' + str(reg)),
                  end='  ')
            if i % 8 == 7:
                print('')

    def print_reg(self, reg_num):
        'Print the content of a single register indicated by the register number `reg_num`.'
        print("{}: {:>8}, value: {:>11d}".format(
            "{}".format(reg_num), '0x' + str(self.regs[reg_num].bitstring.hex),
            str(self.regs[reg_num])))

    def write(self, reg_dst: int, value: BitArray):
        '''Update the target register `reg_dst` with the `value`.
        Args:
          - reg_dst (int): the target register number
          - value (BitArray): the value to write
        '''

        value_str = ''
        if self.reg_symbol == 'f':
            float_value = value.float
            value_str = "float: {}".format(float_value)
        else:
            value_str = "int: {}, uint: {}".format(value.int, value.uint)

        logger.debug("Updating register {}{} with bitstring {} ({}).".format(
            self.reg_symbol, reg_dst, value, value_str))

        self.regs[reg_dst].update_value(value)

    def __getitem__(self, reg_num: int):
        return self.regs[reg_num]

    def read(self, reg_num: int):
        '''Return the bitstring stored in the register `reg_num`
        Args:
          - reg_num (int): the number of the register to read
        Ret: The bitstring (BitArray) stored in this register.
        '''
        return self.regs[reg_num].bitstring
