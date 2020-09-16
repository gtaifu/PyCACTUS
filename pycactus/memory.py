from bitstring import BitArray


class Memory():
    def __init__(self, size: int = 1000000):
        self.size = size
        self._mem = bytearray(size)

    def _check_addr(self, addr):
        if addr < 0:
            raise ValueError("Given address ({}) is less than 0".format(addr))

        if addr >= self.size:
            raise ValueError("Given address ({}) exceeds the maximum memory"
                             " address ({}).".format(addr, self.size-1))

    def _check_word_addr(self, addr):
        if addr < 0:
            raise ValueError("Given address ({}) is less than 0".format(addr))

        if addr >= self.size - 3:
            raise ValueError("Given word address ({}) can cause memory access overflow. "
                             "Maximum memory address is ({}).".format(addr, self.size-1))

    def read_byte(self, addr):
        self._check_addr(addr)
        return BitArray(uint=self._mem[addr], length=8)

    def write_byte(self, addr: int, val: BitArray):
        '''Write a byte into the memory.
        Args:
          - addr (int): the address to write;
          - val (BitArray): an 8-bit bitstring.
        '''
        self._check_addr(addr)
        self._mem[addr] = val.uint

    def read_word(self, addr):
        '''Read four bytes from the memory with the starting address being `addr`.
        The current implementation assumes little-endian format.

        For example, for the following data arrangement:
        ```
         addr    value
        0x4003    0x78
        0x4002    0x56
        0x4001    0x34
        0x4000    0x12
        ```
        When we read the addr 0x4000, the word returned is 0x78563412.
        In other words, the least significant byte is put at the lowest address.
        '''
        self._check_word_addr(addr)
        return (self.read_byte(addr+3) + self.read_byte(addr+2) +
                self.read_byte(addr+1) + self.read_byte(addr))

    def write_word(self, addr: int, val: BitArray):
        '''Write a word into the memory.
        Args:
          - addr (int): the address to write;
          - val (BitArray): a 32-bit, little-endian bitstring.
        '''
        self._check_word_addr(addr)
        self._mem[addr+3] = (val[0:8]).uint
        self._mem[addr+2] = (val[8:16]).uint
        self._mem[addr+1] = (val[16:24]).uint
        self._mem[addr] = (val[24:32]).uint
