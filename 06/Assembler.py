import re
import pathlib
import config
import sys


class Parser:
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            s = f.read()
        s = s.replace(' ', '')
        s = re.sub(r'//.*\n', '\n', s)
        self.lines = s.split('\n')
        self.lines = [line for line in self.lines if line != '']
        self.is_first_run = True
        self.symbol_dic = config.symbol_dic
        self.clearCache()

    def clearCache(self):
        self.output = ""
        # self.input_file_row_idx = 0
        self.output_file_row_idx = 0
        self.memory_iterator = 16

    def combertToBinaryStr(self, num):
        bin_str = format(num, 'b')
        return bin_str.rjust(16, '0')

    def commandType(self):
        if self.line[0] == '@':
            return 'A_COMMAND'
        elif self.line[0] == '(':
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def extractSymbol(self):
        return self.line.translate(str.maketrans({'(': '', ')': '', '@': ''}))

    def updateDbit(self):
        if '=' not in self.line:
            return
        mnemonic = self.line.split('=')[0]
        if mnemonic == 'null':
            return
        if 'A' in mnemonic:
            self.binary[10] = 1
        if 'D' in mnemonic:
            self.binary[11] = 1
        if 'M' in mnemonic:
            self.binary[12] = 1

    def updateCbit(self):
        mnemonic = self.line
        if '=' in mnemonic:
            mnemonic = self.line.split('=')[1]
        if ';' in mnemonic:
            mnemonic = mnemonic.split(';')[0]
        # binary[3] is 1 if comp contains 'M'
        if 'M' in mnemonic:
            self.binary[3] = 1
        mnemonic = mnemonic.replace('M', 'A')
        b = config.comp_dic[mnemonic]
        for i in range(6):
            self.binary[i + 4] = str(b[i])

    def updateJbit(self):
        if ';' not in self.line:
            return
        mnemonic = self.line.split(';')[1]
        b = config.jump_dic[mnemonic]
        self.binary[13] = str(b[0])
        self.binary[14] = str(b[1])
        self.binary[15] = str(b[2])

    def processC(self):
        # The first three bits are 1
        self.binary[0] = 1
        self.binary[1] = 1
        self.binary[2] = 1
        # Update other bits
        self.updateDbit()
        self.updateCbit()
        self.updateJbit()
        if not self.is_first_run:
            self.output += ''.join([str(i) for i in self.binary]) + '\n'

    def processA(self):
        symbol_mnemonic = self.extractSymbol()
        # If the input is like '@10'
        if symbol_mnemonic.isdecimal():
            if int(symbol_mnemonic) < 32768:
                bin_str = self.combertToBinaryStr(int(symbol_mnemonic))
            if not self.is_first_run:
                self.output += bin_str + '\n'
                return
        # If the input is a symble like '@i' or '@40000'
        if symbol_mnemonic in self.symbol_dic:  # If already exist in symbol dic
            if not self.is_first_run:
                self.output += self.symbol_dic[symbol_mnemonic] + '\n'
            return
        else:  # If new symble
            bin_str = self.combertToBinaryStr(self.memory_iterator)
            self.symbol_dic[symbol_mnemonic] = bin_str
            self.memory_iterator += 1
            if not self.is_first_run:
                self.output += bin_str + '\n'
            return

    def processL(self):
        symbol_mnemonic = self.extractSymbol()
        bin_str = self.combertToBinaryStr(self.output_file_row_idx)
        self.symbol_dic[symbol_mnemonic] = bin_str

    def processLine(self):
        self.binary = [0 for i in range(16)]
        command_type = self.commandType()
        # If not L_COMMAND, one row will be added to the output file
        if command_type != 'L_COMMAND':
            self.output_file_row_idx += 1
        if self.is_first_run:
            if command_type == 'L_COMMAND':
                self.processL()
            return
        if command_type == 'C_COMMAND':
            self.processC()
        elif command_type == 'A_COMMAND':
            self.processA()
        else:
            self.processL()
        return

    def saveToFile(self):
        p_file = pathlib.Path(self.path)
        path_w = p_file.with_suffix('.hack')
        with open(path_w, mode='w') as f:
            f.write(self.output)

    def advance(self):
        for line in self.lines:
            self.line = line
            self.processLine()
            # self.input_file_row_idx += 1
        if not self.is_first_run:
            self.saveToFile()
        self.clearCache()
        return


if __name__ == '__main__':
    path = sys.argv[1]
    parser_obj = Parser(path)
    parser_obj.advance()
    parser_obj.is_first_run = False
    parser_obj.advance()
