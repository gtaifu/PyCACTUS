from bitstring import BitArray


class Bit_array_cell():
    def __init__(self, width=32):
        assert(isinstance(width, int))
        # the width is supposed not to change in the future
        self.bitstring = BitArray(width)
        self._width = width

    def __len__(self):
        return self._width

    def check_length(self, other):
        if self.__len__() != len(other):
            raise ValueError("Cannot perform addition on two bitstring with different"
                             " length ({}, {})".format(self.__len__(), len(other)))

    def update_value(self, value: BitArray):
        '''Update the value of this register to `value`.
        Args:
          - value (BitArray): the value to write
        '''
        assert(isinstance(value, BitArray))
        if self._width != len(value):
            raise ValueError("Given value has a bitstring with a different length ({}) "
                             " to the original length ({})".format(len(value), self._width))

        self.bitstring = value

    def __getitem__(self, item):
        return self.bitstring[item]
