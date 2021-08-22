import re
import pathlib
import sys


class CodeWriter:
    def __init__(self, p_path: pathlib.Path) -> None:
        if p_path.is_dir():
            self.path_w = f'{p_path}/{p_path.stem}.asm'
        else:
            self.path_w = p_path.with_suffix('.asm')
        print(self.path_w)
        self.dic = {
            'local': '@LCL',
            'argument': '@ARG',
            'this': '@THIS',
            'that': '@THAT',
            'pointer': '@3',
            'temp': '@5',
        }
        self.snippets = {
            'increment_sp': ['@SP', 'M = M + 1'],
            'decrement_sp': ['@SP', 'M = M - 1'],
            'copy_d_to_stack_top': ['@SP', 'A = M', 'M = D'],
            'from_stack_top_value_to_d': ['@SP', 'A = M', 'D = M'],
            'update_address_to_top': ['@SP', 'A = M'],
            'move_address_backward': ['A = A - 1']
        }
        self.appendix: str = ''
        self.appendix_idx: int = 0
        self.output: str = ''
        self.return_address_idx: int = 0
        self.ret_idx: int = 0
        self.addOutputLines(['@256', 'D = A', '@SP', 'M = D'])
        self.processCall('Sys.init', 0)

    def setFileName(self, p_file: pathlib.Path) -> None:
        self.filename: str = p_file.stem  # get filename

    def processPush(self, arg1: str, arg2: str) -> None:
        if arg1 == 'constant':
            # Place num to stack top. ex) 'push constant 2'
            self.addOutputLines([f'@{arg2}', 'D = A'])
        elif arg1 == 'static':
            # Place the value of a symbol to stack top. ex) 'push static 1'
            # Create the name of the symbol. ex) '@filename.1'
            self.addOutputLines([f'@{self.filename}.{arg2}', 'D = M'])
        elif arg1 == 'pointer' or arg1 == 'temp':
            # Place the address of this (pointer[0]) or that (pointer[1]) to stack top. ex) 'push pointer 1', or
            # Place the value of temp to stack top. ex) 'push temp 1'
            self.addOutputLines([f'@{arg2}', 'D = A', f'{self.dic[arg1]}', 'A = A + D', 'D = M'])
        else:  # argument, local, this, that
            # Place the value of the specified segment[idx] to stack top. ex) 'push argument 3'
            self.addOutputLines([f'@{arg2}', 'D = A', f'{self.dic[arg1]}', 'A = M + D', 'D = M'])
        self.addOutputLines(self.snippets['copy_d_to_stack_top'] + self.snippets['increment_sp'])

    def processPop(self, arg1: str, arg2: str) -> None:
        self.addOutputLines(self.snippets['decrement_sp'] + self.snippets['from_stack_top_value_to_d'])
        if arg1 == 'constant':
            # Remove num from stack top. ex) 'pop constant 2'
            # Is 'pop constant' possible in .vm file?
            self.addOutputLines([f'@{str(arg2)}', 'M = D'])
        elif arg1 == 'static':
            # Place the value of a stack top to a symbol. ex) 'pop static 1'
            # Create the name of the symbol. ex) '@filename.1'
            self.addOutputLines([f'@{self.filename}.{arg2}', 'M = D'])
        else:
            forward_A_arg2_times: list[str] = ['A = A + 1' for _ in range(int(arg2))]
            if arg1 == 'pointer' or arg1 == 'temp':
                # Place the value of the stack top to this (pointer[0]) or that (pointer[1]). ex) 'pop pointer 1', or
                # Place the value of the stack top to temp. ex) 'pop temp 1'
                self.addOutputLines([f'{self.dic[arg1]}'] + forward_A_arg2_times + ['M = D'])
            else:  # argument, local, this, that
                # Place the value of the stack top to specified segment[idx]. ex) 'pop argument 3'
                self.addOutputLines([f'{self.dic[arg1]}', 'A = M'] + forward_A_arg2_times + ['M = D'])

    def processArithmetric(self, command: str) -> None:
        if command == 'neg' or command == 'not':
            self.addOutputLines(self.snippets['update_address_to_top'] + self.snippets['move_address_backward'])
            self.addOutputLines(['M = -M'] if command == 'neg' else ['M = !M'])
            return
        self.addOutputLines(
            self.snippets['decrement_sp']
            + self.snippets['from_stack_top_value_to_d']  # set the value of the second operand to D
            + self.snippets['move_address_backward'])  # move address to the first operand
        if command == 'add':
            self.addOutputLines(['M = M + D'])
        elif command == 'sub':
            self.addOutputLines(['M = M - D'])
        elif command == 'and':
            self.addOutputLines(['M = D & M'])
        elif command == 'or':
            self.addOutputLines(['M = D | M'])
        else:  # eq, gt, lt
            self.addOutputLines(['D = M - D', f'@TRUE{self.appendix_idx}'])
            if command == 'eq':
                self.addOutputLines(['D;JEQ'])
            if command == 'gt':
                self.addOutputLines(['D;JGT'])
            if command == 'lt':
                self.addOutputLines(['D;JLT'])
            # If false, write 0 (false) to the top of the stuck
            self.addOutputLines(['@SP', 'A = M - 1', 'M = 0', f'(BACK{str(self.appendix_idx)})'])
            # If true, write -1 (true) to the top of the stuck
            self.addAppendixLines([f'(TRUE{self.appendix_idx})', '@SP', 'A = M - 1',
                                   'M = -1', f'@BACK{str(self.appendix_idx)}', '0;JMP'])
            self.appendix_idx += 1

    def processLabel(self, arg1: str) -> None:
        # ex) label loop
        self.addOutputLines([f'({arg1})'])

    def processGoto(self, arg1: str) -> None:
        # ex) goto loop
        self.addOutputLines([f'@{arg1}', '0;JMP'])

    def processIfGoto(self, arg1: str) -> None:
        # ex) if-goto loop
        self.addOutputLines(['@SP', 'A = M - 1', 'D = M'] +
                            [f'@TRUE{self.appendix_idx}', 'D;JNE'] +
                            self.snippets['decrement_sp'])
        self.addAppendixLines([f'(TRUE{self.appendix_idx})'] + self.snippets['decrement_sp'] + [f'@{arg1}', '0;JMP'])
        self.appendix_idx += 1

    def processFunction(self, arg1: str, arg2: str) -> None:
        self.addOutputLines([f'({arg1})'])
        for i in range(int(arg2)):
            self.processPush('constant', 0)
            self.processPush('local', i)

    def processReturn(self) -> None:
        updateAddressToOriginal = lambda label, times: self.addOutputLines(
            ['@LCL', 'A = M'] + ['A = A - 1' for _ in range(times)] + ['D = M', f'@{label}', 'M = D'])
        # Place return value to argument 0
        updateAddressToOriginal(f'ret{self.ret_idx}', 5)  # ret = *(LCL - 5)
        self.processPop('argument', '0')  # *ARG = pop()
        self.addOutputLines(['@ARG', 'D = M + 1', '@SP', 'M = D'])  # SP = ARG + 1
        # updateAddressToOriginal(f'ret', 5)  # ret = *(LCL - 5)
        updateAddressToOriginal('THAT', 1)  # THAT = *(LCL - 1)
        updateAddressToOriginal('THIS', 2)  # THIS = *(LCL - 2)
        updateAddressToOriginal('ARG', 3)  # ARG = *(LCL - 3)
        updateAddressToOriginal('LCL', 4)  # LCL = *(LCL - 4)
        # self.addOutputLines([f'@ret', 'A = M', '0;JMP'])  # goto ret
        self.addOutputLines([f'@ret{self.ret_idx}', 'A = M', '0;JMP'])  # goto ret
        self.ret_idx += 1

    def processCall(self, arg1: str, arg2: str):
        # self.processPush('constant', self.getLineNum() + 50 + int(arg2))  # push return_address
        # arg2 = max(int(arg2), 1)
        self.addOutputLines(
            [f'@return_address_{self.return_address_idx}', 'D = A'] +
            self.snippets['copy_d_to_stack_top'] +
            self.snippets['increment_sp'])  # push return-address
        pushLabel = lambda label: self.addOutputLines(
            [f'@{label}', 'D = M'] +
            self.snippets['copy_d_to_stack_top'] +
            self.snippets['increment_sp'])
        pushLabel('LCL')  # push LCL
        pushLabel('ARG')  # push ARG
        pushLabel('THIS')  # push THIS
        pushLabel('THAT')  # push THAT
        self.addOutputLines(['@SP', 'D = M'] +
                            ['D = D - 1' for _ in range(int(arg2) + 5)] +
                            ['@ARG', 'M = D'])  # ARG = SP - arg2 - 5
        self.addOutputLines(['@SP', 'D = M', '@LCL', 'M = D'])  # LCL = SP
        self.processGoto(arg1)  # goto f
        self.addOutputLines([f'(return_address_{self.return_address_idx})'])
        self.return_address_idx += 1

    def getLineNum(self) -> int:
        return len(self.output.split('\n'))

    def addOutputLines(self, lines: 'list[str]') -> None:
        self.output += '\n'.join(lines) + '\n'

    def addAppendixLines(self, lines: 'list[str]') -> None:
        self.appendix += '\n'.join(lines) + '\n'

    def saveToFile(self) -> None:
        if self.appendix != '':
            self.output += '@END\n0;JMP\n' + self.appendix + '(END)\n'
        with open(self.path_w, mode='w') as f:
            f.write(self.output)


class Parser:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.p_file = pathlib.Path(self.path)
        with open(path) as f:
            s: str = f.read()
        s = re.sub(r'//.*\n', '\n', s)  # delete comments
        s = re.sub(r' *\n', '\n', s)  # delete spaces at the end of lines
        self.lines: list[str] = s.split('\n')
        self.lines = [line for line in self.lines if line != '']  # delete black lines
        self.line = self.lines[0]
        self.line_num = len(self.lines)
        self.current_line_num = 0

    def commandType(self) -> str:
        """
        Determine command type from a line
        """
        command: str = self.line.split(' ')[0]
        if command == 'push':
            return 'C_PUSH'
        elif command == 'pop':
            return 'C_POP'
        elif command == 'label':
            return 'C_LABEL'
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

    def arg1(self) -> str:
        """
        Returns the first argument
        """
        tmp = self.line.split(' ')
        if len(tmp) != 1:  # ex) 'local' in 'push local 0'
            return tmp[1]
        else:  # When C_ARITHMETIC, the command itself is returned. ex) 'add'
            return tmp[0]

    def arg2(self) -> str:
        """
        Returns the second argument.
        This is called only when 'C_PUSH', 'C_POP', 'C_FUNCTION', or 'C_CALL'
        """
        # ex) '0' in 'push local 0'
        tmp = self.line.split(' ')
        return tmp[2]

    def hasMoreCommands(self) -> bool:
        return True if self.current_line_num < self.line_num else False

    def advance(self) -> bool:
        print(self.current_line_num)
        self.line = self.lines[self.current_line_num]
        self.current_line_num += 1


if __name__ == '__main__':
    path: str = sys.argv[1]
    p_path: pathlib.Path = pathlib.Path(path)
    p_file_list: 'list[pathlib.Path]' = []
    if p_path.is_dir():
        p_file_list = list(p_path.glob('**/*.vm'))
    else:
        p_file_list = [p_path]

    writer = CodeWriter(p_path)
    for p_file in p_file_list:
        parser = Parser(p_file)
        writer.setFileName(p_file)
        while parser.hasMoreCommands():
            parser.advance()
            command_type: str = parser.commandType()
            if command_type == 'C_ARITHMETIC':
                writer.processArithmetric(parser.arg1())
            elif command_type == 'C_PUSH':
                writer.processPush(parser.arg1(), parser.arg2())
            elif command_type == 'C_POP':
                writer.processPop(parser.arg1(), parser.arg2())
            elif command_type == 'C_LABEL':
                writer.processLabel(parser.arg1())
            elif command_type == 'C_GOTO':
                writer.processGoto(parser.arg1())
            elif command_type == 'C_IF':
                writer.processIfGoto(parser.arg1())
            elif command_type == 'C_FUNCTION':
                writer.processFunction(parser.arg1(), parser.arg2())
            elif command_type == 'C_RETURN':
                writer.processReturn()
            elif command_type == 'C_CALL':
                writer.processCall(parser.arg1(), parser.arg2())
                print(parser.arg1(), ',', parser.arg2())
    writer.saveToFile()
