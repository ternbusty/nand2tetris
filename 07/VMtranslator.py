import re
import pathlib
import sys

increment_sp = '@SP\nM = M + 1\n'
decrement_sp = '@SP\nM = M - 1\n'

update_top_to_d = '@SP\nA = M\nM = D\n'
update_d_to_top = '@SP\nA = M\nD = M\n'

update_address_to_top = '@SP\nA = M\n'
move_address_backward = 'A = A - 1\n'


class Parser:
    def __init__(self, path):
        self.path = path
        self.p_file = pathlib.Path(self.path)
        with open(path) as f:
            s = f.read()
        s = re.sub(r'//.*\n', '\n', s)  # delete comments
        s = re.sub(r' *\n', '\n', s)  # delete spaces at the end of the lines
        self.lines = s.split('\n')
        # delete black lines
        self.lines = [line for line in self.lines if line != '']
        print(self.lines)
        self.output = ''
        self.appendix_idx = 0
        self.appendix_first = '@END\n0;JMP\n'
        self.appendix = ''
        self.appendix_last = '(END)\n'

    def processPushPop(self, arg1, arg2, is_push):
        dic = {
            'local': '@LCL',
            'argument': '@ARG',
            'this': '@THIS',
            'that': '@THAT',
            'pointer': '@3',
            'temp': '@5',
        }
        if not is_push:
            self.output += decrement_sp + update_d_to_top
        if arg1 == 'constant':
            self.output += '@' + str(arg2)
            if is_push:
                self.output += '\nD = A\n'
            else:
                self.output += '\nM = D\n'
        else:
            if arg1 == 'static':
                filename = self.p_file.stem
                self.output += '@' + filename + '.' + str(arg2)
                if is_push:
                    self.output += '\nD = M\n'
                else:
                    self.output += '\nM = D\n'
            elif arg1 == 'pointer' or arg1 == 'temp':
                if is_push:
                    self.output += '@' + \
                        str(arg2) + '\nD = A\n' + dic[arg1] + '\nA = A + D\nD = M\n@SP\nA = M\nM = D\n'
                else:
                    self.output += '@' + \
                        str(arg2) + '\nD = A\n' + dic[arg1] + '\nD = A + D\n@R13\nM = D\n@SP\nA = M\nD = M\n@R13\nA = M\nM = D\n'
            else:
                if is_push:
                    self.output += '@' + \
                        str(arg2) + '\nD = A\n' + dic[arg1] + '\nA = M + D\nD = M\n@SP\nA = M\nM = D\n'
                else:
                    self.output += '@' + \
                        str(arg2) + '\nD = A\n' + dic[arg1] + '\nD = M + D\n@R13\nM = D\n@SP\nA = M\nD = M\n@R13\nA = M\nM = D\n'
        if is_push:
            self.output += update_top_to_d + increment_sp

    def processArithmetric(self, command):
        # If 'neg' or 'not', we don't need to decrement sp
        if command == 'neg' or command == 'not':
            self.output += update_address_to_top + move_address_backward
            if command == 'neg':
                self.output += 'M = -M\n'
            else:
                self.output += 'M = !M\n'
            return
        self.output += decrement_sp
        # D = Stack[top], M = Stack[top - 1]
        self.output += update_d_to_top + move_address_backward
        if command == 'add':
            self.output += 'M = M + D\n'
        elif command == 'sub':
            self.output += 'M = M - D\n'
        elif command == 'and':
            self.output += 'M = D & M\n'
        elif command == 'or':
            self.output += 'M = D | M\n'
        else:
            self.appendix += '(TRUE' + str(self.appendix_idx) + \
                ')\n@SP\nA = M - 1\nM = -1\n@BACK' + str(self.appendix_idx) + '\n0;JMP\n'
            if command == 'eq':
                self.output += 'D = M - D\n@TRUE' + \
                    str(self.appendix_idx) + '\nD;JEQ\n@SP\nA = M - 1\nM = 0\n(BACK' + str(self.appendix_idx) + ')\n'
            if command == 'gt':
                self.output += 'D = M - D\n@TRUE' + \
                    str(self.appendix_idx) + '\nD;JGT\n@SP\nA = M - 1\nM = 0\n(BACK' + str(self.appendix_idx) + ')\n'
            if command == 'lt':
                self.output += 'D = M - D\n@TRUE' + \
                    str(self.appendix_idx) + '\nD;JLT\n@SP\nA = M - 1\nM = 0\n(BACK' + str(self.appendix_idx) + ')\n'
            self.appendix_idx += 1

    def commandType(self):
        command = self.line.split(' ')[0]
        if command == 'push':
            return 'C_PUSH'
        elif command == 'pop':
            return 'C_POP'
        elif command == 'label':
            return 'C_label'
        elif command == 'goto':
            return 'C_GOTO'
        elif command == 'if-goto':
            return 'C_IF'
        elif command == 'function':
            return 'C_FUNCTION'
        elif command == 'return':
            return 'C_RETURN'
        elif command == 'call':
            return 'C_CALL'
        else:
            return 'C_ARITHMETIC'

    def getArg1(self):
        tmp = self.line.split(' ')
        if len(tmp) != 1:
            return tmp[1]
        else:
            return tmp[0]

    # Called only when 'C_PUSH', 'C_POP', 'C_FUNCTION', or 'C_CALL'
    def getArg2(self):
        tmp = self.line.split(' ')
        return tmp[2]

    def processLine(self):
        command_type = self.commandType()
        print(command_type)
        if command_type == 'C_ARITHMETIC':
            self.processArithmetric(self.line)
        if command_type == 'C_PUSH':
            arg1 = self.getArg1()
            arg2 = self.getArg2()
            self.processPushPop(arg1, arg2, is_push=True)
        elif command_type == 'C_POP':
            arg1 = self.getArg1()
            arg2 = self.getArg2()
            self.processPushPop(arg1, arg2, is_push=False)

    def saveToFile(self):
        path_w = self.p_file.with_suffix('.asm')
        if self.appendix != '':
            self.output += self.appendix_first + self.appendix + self.appendix_last
        with open(path_w, mode='w') as f:
            f.write(self.output)

    def advance(self):
        for line in self.lines:
            self.line = line
            self.processLine()
        self.saveToFile()
        return


if __name__ == '__main__':
    path = sys.argv[1]
    parser_obj = Parser(path)
    parser_obj.advance()
