import re
import pathlib
import config
import sys


class CParser():
    def __init__(self, line: str, binary_list: 'list[int]') -> None:
        self.line = line
        self.binary_list = binary_list

    def updateDbit(self) -> None:
        """
        Update binary_list when dest exists (when '=' is in the line)
        """
        if '=' not in self.line:
            return
        # Extract left side of the '=' (dest)
        mnemonic: str = self.line.split('=')[0]
        # if mnemonic == 'null':
        #     return
        if 'A' in mnemonic:
            self.binary_list[10] = 1
        if 'D' in mnemonic:
            self.binary_list[11] = 1
        if 'M' in mnemonic:
            self.binary_list[12] = 1

    def updateCbit(self) -> None:
        """
        Update binary_list following the C bits in the line
        """
        # extract between '=' and ';'
        mnemonic: str = self.line
        if '=' in mnemonic:
            mnemonic = self.line.split('=')[1]
        if ';' in mnemonic:
            mnemonic = mnemonic.split(';')[0]
        # binary[3] (a) is 1 if comp contains 'M'
        if 'M' in mnemonic:
            self.binary_list[3] = 1
        # Convert 'M' to 'A' in order to refer to comp_dic
        mnemonic = mnemonic.replace('M', 'A')
        # Refer to comp_dic and fill in the comp binary
        b: str = config.comp_dic[mnemonic]
        for i in range(6):
            self.binary_list[i + 4] = str(b[i])

    def updateJbit(self) -> None:
        """
        Update binary_list when jump exists (when ';' is in the line)
        """
        if ';' not in self.line:
            return
        mnemonic: str = self.line.split(';')[1]
        b = config.jump_dic[mnemonic]
        self.binary_list[13] = str(b[0])
        self.binary_list[14] = str(b[1])
        self.binary_list[15] = str(b[2])

    def process(self) -> 'list[int]':
        # The first three bits are 1
        self.binary_list[0] = self.binary_list[1] = self.binary_list[2] = 1
        # Update other bits
        self.updateDbit()
        self.updateCbit()
        self.updateJbit()
        return self.binary_list


class Parser:
    def __init__(self, path: str) -> None:
        self.path: str = path
        with open(path) as f:
            s: str = f.read()
        s = s.replace(' ', '')  # delete whitespaces
        s = re.sub(r'//.*\n', '\n', s)  # delete comments
        self.lines: list[str] = [line for line in s.split('\n') if line != '']  # split by \n and delete black lines
        self.symbol_dic: dict[str, str] = config.symbol_dic
        self.clearCache()

    def clearCache(self) -> None:
        self.output: str = ""
        self.output_file_row_idx: int = 0
        self.next_memory_idx: int = 16

    def combertNumToBinaryStr(self, num: int) -> str:
        bin_str: str = format(num, 'b')
        return bin_str.rjust(16, '0')

    def commandType(self) -> str:
        if self.line[0] == '@':
            return 'A_COMMAND'
        elif self.line[0] == '(':
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def extractSymbol(self) -> str:
        # Extract symbol str from L_COMMAND or A_COMMAND
        return self.line.translate(str.maketrans({'(': '', ')': '', '@': ''}))

    def processC(self) -> str:
        """
        Process lines that do not start with neither '@' nor '('
        """
        c_parser_obj = CParser(self.line, self.binary_list)
        self.binary_list = c_parser_obj.process()
        return ''.join([str(i) for i in self.binary_list])

    def processA(self) -> str:
        """
        Process lines that start with '@'
        """
        # Extract symbol str
        symbol_mnemonic: str = self.extractSymbol()
        # If the input is like '@10'
        if symbol_mnemonic.isdecimal():
            # If the number is more than 32678, it is invalid as an ROM address and is regarded as a symbol
            if int(symbol_mnemonic) < 32768:
                bin_str = self.combertNumToBinaryStr(int(symbol_mnemonic))
                return bin_str
        # If the input is a symbol like '@i' or '@40000'
        # If already exist in symbol dic
        if symbol_mnemonic in self.symbol_dic:
            return self.symbol_dic[symbol_mnemonic]
        # If new symbol
        bin_str = self.combertNumToBinaryStr(self.next_memory_idx)
        self.symbol_dic[symbol_mnemonic] = bin_str
        self.next_memory_idx += 1
        return bin_str

    def processL(self) -> None:
        """
        Process lines that start with '('
        """
        # Extract symbol str
        symbol_mnemonic: str = self.extractSymbol()
        # Convert the ROM address to binary string
        bin_str: str = self.combertNumToBinaryStr(self.output_file_row_idx)
        # Update symbol_dic
        self.symbol_dic[symbol_mnemonic] = bin_str

    def saveToFile(self) -> None:
        p_file = pathlib.Path(self.path)
        path_w: pathlib.Path = p_file.with_suffix('.hack')
        with open(path_w, mode='w') as f:
            f.write(self.output)

    def firstRun(self) -> None:
        # In the first run, only L_COMMAND is processed
        for line in self.lines:
            self.line = line
            if line[0] == '(':
                self.processL()
            else:
                self.output_file_row_idx += 1
        self.clearCache()
        return

    def secondRun(self) -> None:
        for line in self.lines:
            self.line = line
            self.binary_list: list[int] = [0 for _ in range(16)]
            command_type: str = self.commandType()
            if command_type == 'L_COMMAND':
                continue
            # If not L_COMMAND, one row will be added to the output file
            self.output_file_row_idx += 1
            result: str = ''
            if command_type == 'C_COMMAND':
                result = self.processC()
            else:
                result = self.processA()
            self.output += result + '\n'
        self.saveToFile()
        self.clearCache()
        return


if __name__ == '__main__':
    path = sys.argv[1]
    parser_obj = Parser(path)
    parser_obj.firstRun()
    parser_obj.secondRun()
