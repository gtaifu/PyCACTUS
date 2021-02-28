import logging
from types import prepare_class
from bitstring import BitArray
from .data_transfer import Data_transfer
from .utils import get_logger
logger = get_logger((__name__).split('.')[-1])


class Memory():
    def __init__(self, size: int = 1000000, parent_qcp=None):
        self.size = size
        self._mem = bytearray(size)
        self.parent_qcp = parent_qcp
        self.export_history = []
        self.max_export_show_addr = 100

    def final_dump(self):
        for msg in self.export_history:
            print(msg)
            logger.debug(msg)

    def decode_data(self, addr, data_type):
        logger.debug('decoding data at 0x{:x}'.format(addr))
        data_trans = Data_transfer()
        data_trans.set_data_block(self._mem)
        pydata = data_trans.bin_to_pydata(data_type, addr)
        logger.debug('value: {}'.format(pydata))

    def dump_content(self, data_addr, data_type):
        start_addr = (data_addr // 16) * 16
        no_line_to_print = 4
        head = ''.join(['{:5x}'.format(i) for i in range(16)])
        logger.debug(" addr:" + head)
        logger.debug(
            '--------------------------------------------------------------------------------------')
        for line_no in range(no_line_to_print):
            start = '{:5x}:'.format(start_addr+line_no)
            cells = ''.join(['{:>5s}'.format('{:d}'.format(
                self._mem[start_addr + offset + line_no*16]))
                for offset in range(16)])
            logger.debug(start + cells)

    def get_entire_mem(self):
        return self._mem

    def set_log_level(self, level):
        logger.setLevel(level)

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
        msg = "Memory write (addr: 0x{:x})  <--  (byte: 0x{:x}).\n".format(addr, val.int)
        logger.debug(msg)
        if (addr < self.max_export_show_addr):
            self.export_history.append(msg[:-1])

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
        msg = "Memory write (addr: 0x{:x})  <--  (word: 0x{:x}).\n".format(addr, val.int)
        logger.debug(msg)
        if (addr < self.max_export_show_addr):
            self.export_history.append(msg[:-1])
        self._mem[addr+3] = (val[0:8]).uint
        self._mem[addr+2] = (val[8:16]).uint
        self._mem[addr+1] = (val[16:24]).uint
        self._mem[addr] = (val[24:32]).uint
