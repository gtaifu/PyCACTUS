import logging
from bitstring import BitArray
from pycactus.utils import get_logger

logger = get_logger((__name__).split('.')[-1])


class Bit_array_cell():
    def __init__(self, width=32):
        assert(isinstance(width, int))
        # the width is supposed not to change in the future
        self.uint = 0
        self.int = 0
        self.update_value(BitArray(length=width))
        self._width = width

    @classmethod
    def reg_symbol(cls):
        raise NotImplementedError

    def __len__(self):
        return self._width

    def check_length(self, other):
        # comment the following code to improve execution speed.
        # if self.__len__() != len(other):
        #     raise ValueError("Cannot perform addition on two bitstring with different"
        #                      " length ({}, {})".format(self.__len__(), len(other)))
        pass

    def update_value(self, value: BitArray):
        '''Update the value of this register to `value`.
        Args:
          - `value` (BitArray): the value to write
        '''
        assert(isinstance(value, BitArray))
        # if self._width != len(value):
        #     raise ValueError("Given value has a bitstring with a different length ({}) "
        #                      " to the original length ({})".format(len(value), self._width))

        self.bitstring = value
        self.uint = self.bitstring.uint
        self.int = self.bitstring.int

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
        self.set_log_level(logging.WARNING)

    def set_log_level(self, level):
        logger.setLevel(level)

    def __str__(self):
        '''Dump the content of the entire register file.'''
        my_str = ''
        for i, reg in enumerate(self.regs):
            my_str += '{:>15}  '.format(self.reg_symbol + str(i) + ': ' + str(reg))
            if i % 8 == 7:
                my_str += '\n'
        return my_str

    def __obj_str__(self):
        '''Dump the content of the entire register file.'''
        my_str = ''
        for i, reg in enumerate(self.regs):
            my_str += '{:>15}  '.format(self.reg_symbol + str(i) + ': {}'.format(reg.bitstring))
            if i % 8 == 7:
                my_str += '\n'
        return my_str

    def dump(self):
        'Dump the content of the entire register file.'
        print(self.__str__())

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

        if logger.level is logging.DEBUG:
            value_str = ''
            if self.reg_symbol == 'f':
                float_value = value.float
                value_str = "float: {}".format(float_value)
            else:
                value_str = "int: {}, uint: {}".format(value.int, value.uint)

            # logger.debug("Updating register {}{} with bitstring {} ({}).\n".format(
            #     self.reg_symbol, reg_dst, value, value_str))
            logger.debug("{:>3s}  <--  {} ({}).\n".format(
                '{}{}'.format(self.reg_symbol, reg_dst), hex(value.int), value.int))

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
