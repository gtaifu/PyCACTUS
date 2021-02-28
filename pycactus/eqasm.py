from .eqasm_parser import Eqasm_parser


class Eqasm:
    """eQASM instructions."""

    def __init__(self, filename=None, data=None):
        """Converte eQASM files into instructions."""
        if filename is None and data is None:
            raise ValueError("Missing input file and/or data")
        if filename is not None and data is not None:
            raise ValueError("File and data must not both be specified"
                             "initializing qasm")
        self._filename = filename
        self._data = data

    def return_filename(self):
        """Return the filename."""
        return self._filename

    # def generate_tokens(self):
    #     """Returns a generator of the tokens."""
    #     if self._filename:
    #         with open(self._filename) as ifile:
    #             self._data = ifile.read()

    #     with Eqasm_parser(self._filename) as eqasm_p:
    #         return eqasm_p.read_tokens()

    def parse(self):
        """Parse the data."""
        if self._filename:
            with open(self._filename) as ifile:
                self._data = ifile.read()

        with Eqasm_parser(self._filename) as eqasm_p:
            eqasm_p.parse_debug(False)
            return eqasm_p.parse(self._data)
