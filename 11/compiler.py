import pathlib
import sys
from xmlrpc.client import boolean
from tokenizer import JackTokenizer
from symbolTable import SymbolTable


class CompilationEngine:
    def __init__(self, symbol_table: SymbolTable, p_file: str) -> None:
        self.p_file = p_file
        self.statement_keyword_dic = {
            'let': self.compileLet,
            'if': self.compileIf,
            'while': self.compileWhile,
            'do': self.compileDo,
            'return': self.compileReturn}
        self.binary_operator_dic = {
            '+': 'add',
            '-': 'sub',
            '=': 'eq',
            '>': 'gt',
            '<': 'lt',
            '&': 'and',
            '|': 'or',
            '*': 'call Math.multiply 2',  # The number of local arguments is 2
            '/': 'call Math.divide 2'
        }
        # self.output = self.class_name = self.class_b_str = self.class_e_str = ''
        self.output = ''
        self.output_line_list = []
        self.output_line_cnt = 0
        self.parameter_cnt = 0
        self.while_cnt = self.if_cnt = 0
        self.symbol_table = symbol_table
        tokenizer = JackTokenizer(p_file)
        while tokenizer.hasMoreLine():
            tokenizer.advance()
        self.token_objects = tokenizer.token_objects
        pass

    def compile(self, is_first_run=False):
        self.is_first_run = is_first_run
        self.compileClasses(0, len(self.token_objects) - 1)

    def compileClasses(self, start: int, end_script: int):
        if start >= end_script:
            return
        closing_class_idx = self.compileClass(start, end_script)
        return self.compileClasses(closing_class_idx + 1, end_script)

    def compileClass(self, start: int, end_script: int):
        """
        'class' className '{' classVarDec* subroutineDec* '}'
        ex) class Bar {...}
        """
        self.class_name = self.token_objects[start + 1].token
        self.symbol_table.clearClassScope()
        self.field_cnt = 0
        closing_class_body_idx: int = self.findClosingBracket(start + 2, end_script, '{', '}')
        self.compileClassBody(start + 3, closing_class_body_idx - 1)
        return closing_class_body_idx

    def compileClassBody(self, start: int, end_class_body: int):
        """
        classVarDec* subroutineDec*
        'static int a; method int hoge (...) {...}'
        """
        if start >= end_class_body:
            return
        first_token: str = self.token_objects[start].token
        if first_token in ['static', 'field']:
            end_idx: int = self.compileClassVarDec(start, end_class_body)
        else:
            end_idx: int = self.compileSubroutineDec(start, end_class_body)
        return self.compileClassBody(end_idx + 1, end_class_body)

    def compileClassVarDec(self, start: int, end_class_body: int) -> int:
        """
        ('static' | 'field') type varName (',' varName) * ';'
        ex) 'static int a;'
        """
        kind: str = self.token_objects[start].token.upper()
        type: str = self.token_objects[start + 1].token
        idx: int = start + 2
        while idx <= end_class_body:
            if self.token_objects[idx].token == ';':
                break
            if self.token_objects[idx].token_type == 'IDENTIFIER':
                varname: str = self.token_objects[idx].token
                self.symbol_table.define(varname, type, kind)
                if kind == 'FIELD':
                    self.field_cnt += 1
            idx += 1
        return idx

    def compileSubroutineDec(self, start: int, end_class_body: int) -> int:
        """
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' '{' subroutineBody '}'
        ex) 'method int hoge (...) {...}'
        """
        # Look for the end of the parameter list
        closing_param_list_idx: int = self.findClosingBracket(start + 3, end_class_body, '(', ')')
        # Look for the end of the subroutine body
        closing_subr_body_idx: int = self.findClosingBracket(closing_param_list_idx + 1, end_class_body, '{', '}')
        # Register to subroutine dictionary
        subroutine_kind = self.token_objects[start + 0].token
        subroutine_type = self.token_objects[start + 1].token
        subroutine_name = self.token_objects[start + 2].token
        if self.is_first_run:
            print(self.class_name, subroutine_name)
            self.symbol_table.defineSubroutine(self.class_name, subroutine_name, subroutine_type, subroutine_kind)
            return closing_subr_body_idx
        # Clear symbol table
        self.symbol_table.clearSubroutineScope()
        self.while_cnt = self.if_cnt = 0
        # Declare function
        dec_line_num: int = self.addOutputLines(
            [f'function {self.class_name}.{subroutine_name} LOCAL_VAR_CNT']) - 1
        # If contructor, alloc the class variables
        if (subroutine_kind == 'constructor') and (self.field_cnt != 0):
            self.addOutputLines([f'push constant {self.field_cnt}', 'call Memory.alloc 1', 'pop pointer 0'])
        # If method, push the first argument (instance)
        if subroutine_kind == 'method':
            self.addOutputLines(['push argument 0', 'pop pointer 0'])
        # Compile parameterList
        if subroutine_kind == 'method':
            self.symbol_table.arg_num = 1
        self.compileParameterList(start + 4, closing_param_list_idx - 1)
        # Compile subroutineBody
        self.compileSubroutineBody(closing_param_list_idx + 2, closing_subr_body_idx - 1)
        # Replace LOCAL_VAR_CNT to symbol_table.local_num
        self.output_line_list[dec_line_num] = f'function {self.class_name}.{subroutine_name} {self.symbol_table.local_num}'
        return closing_subr_body_idx

    def compileSubroutineBody(self, start: int, end_body: int) -> None:
        """
        varDec* statements
        ex) 'var int a; let a = 1; return a;'
        """
        if start >= end_body:
            return
        first_token: str = self.token_objects[start].token
        if first_token == 'var':  # varDec
            end_idx: int = self.compileVarDec(start, end_body)
            return self.compileSubroutineBody(end_idx + 1, end_body)
        else:  # statements
            end_idx = self.compileStatements(start, end_body)
            return

    def compileSubroutineCall(self, start: int, end: int) -> None:
        """
        subroutineName '(' expressionList ')' |
        (className | varName) '.' subroutineName '(' expressionList ')'
        ex) 'run()', 'a.run()'
        """
        # Process (className | varName) '.' subroutineName
        call_str = None
        is_method: bool = False
        if self.token_objects[start + 1].token != '.':  # run()
            is_method = True
            subroutine_name = self.token_objects[start].token
            self.addOutputLines(['push pointer 0'])
            call_str = f'call {self.class_name}.{subroutine_name} '
        else:
            # a.run()
            class_or_instance_name = self.token_objects[start].token
            subroutine_name = self.token_objects[start + 2].token
            # When a is an instance and run() is a method
            for scope in [self.symbol_table.subroutine_scope, self.symbol_table.class_scope]:
                if class_or_instance_name in scope.keys():
                    is_method = True
                    item: dict = scope[class_or_instance_name]
                    self.addOutputLines([f'push {item["kind_alias"]} {item["num"]}'])  # push the instance
                    call_str = f'call {item["type"]}.{subroutine_name} '
                    break
            else:  # When a is a class name and run() is a constructor or a function
                call_str = f'call {class_or_instance_name}.{subroutine_name} '
        # Compile expressionList
        idx: int = start
        while self.token_objects[idx].token != '(':
            idx += 1
        closing_expression_list = self.findClosingBracket(idx, end, '(', ')')
        self.compileExpressionList(idx + 1, closing_expression_list - 1)
        # Compile call
        parameter_cnt = self.parameter_cnt + (1 if is_method else 0)
        self.addOutputLines([call_str + str(parameter_cnt)])

    def compileExpressionList(self, start: int, end: int) -> None:
        """
        Split expression list by ',' and process by compileExpression
        """
        self.parameter_cnt = 0
        if start > end:
            return
        idx: int = start
        exp_start_idx: int = start
        while idx <= end:
            if self.token_objects[idx].token == ',':
                self.compileExpression(exp_start_idx, idx - 1)
                exp_start_idx = idx + 1
                self.parameter_cnt += 1
            idx += 1
        self.compileExpression(exp_start_idx, end)
        self.parameter_cnt += 1

    def compileParameterList(self, start: int, end: int) -> None:
        """
        ((type varName) (',' type varName)*)?
        ex) 'int a, char c', ''
        """
        idx: int = start
        name = type = None
        while idx <= end:
            type = self.token_objects[idx].token
            name = self.token_objects[idx + 1].token
            self.symbol_table.define(name, type, 'ARG')
            idx += 3

    def compileVarDec(self, start: int, end_body: int) -> int:
        """
        'var' type varName (',' varname)* ';'
        ex) 'var int a, b;';
        """
        type: str = self.token_objects[start + 1].token
        idx: int = start + 2
        while idx <= end_body:
            if self.token_objects[idx].token == ';':
                break
            if self.token_objects[idx].token_type == 'IDENTIFIER':
                name: str = self.token_objects[idx].token
                self.symbol_table.define(name, type, 'VAR')
            idx += 1
        return idx

    def compileStatements(self, start: int, end_statements: int) -> None:
        """
        Call (compileLet | compileIf | compileWhile | compileDo | compileReturn) and
        process statements recursively
        """
        if start >= end_statements:
            return
        # Decide which function to call by its first token
        first_token: str = self.token_objects[start].token
        end_statement: int = self.statement_keyword_dic[first_token](start, end_statements)
        self.compileStatements(end_statement + 1, end_statements)

    def compileDo(self, start: int, end_statements: int) -> int:
        """
        'do' subroutineCall ';'
        """
        idx: int = start
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.compileSubroutineCall(start + 1, idx - 1)
        self.addOutputLines(['pop temp 0'])
        return idx

    def compileLet(self, start: int, end_statements: int) -> int:
        """
        'let' varname ('[' expression ']')? '=' expression ';'
        ex) 'let a[1] = b + c;'
        """
        # Process varname
        varname: str = self.token_objects[start + 1].token
        item: dict = self.symbol_table.refer(varname)
        # Detect the start of the right operand
        right_operand_start_idx: int = None
        is_exp_in_left: bool = False
        # If expression is in the left operand
        if self.token_objects[start + 2].token == '[':  # If expression in the left operand
            is_exp_in_left = True
            # Process expression in the left operand
            closing_expression_idx = self.findClosingBracket(start + 2, end_statements, '[', ']')
            self.compileExpression(start + 3, closing_expression_idx)
            # Push the array var
            self.addOutputLines([f'push {item["kind_alias"]} {item["num"]}'])
            # Use 'that' segment to access varname[expression]
            self.addOutputLines(['add'])
            right_operand_start_idx = closing_expression_idx + 2
        else:  # If no expression in the reft operand
            right_operand_start_idx = start + 3
        # Process right operand
        idx: int = right_operand_start_idx
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.compileExpression(right_operand_start_idx, idx - 1)
        if is_exp_in_left:
            self.addOutputLines(['pop temp 0', 'pop pointer 1', 'push temp 0', 'pop that 0'])
        else:
            self.addOutputLines([f'pop {item["kind_alias"]} {item["num"]}'])
        return idx

    def compileWhile(self, start: int, end_statements: int) -> int:
        """
        'while' '(' expression ')' '{' statements '}'
        """
        self.while_cnt += 1
        org_while_cnt = self.while_cnt
        self.addOutputLines([f'label WHILE_EXP{org_while_cnt - 1}'])
        # (expression)
        closing_expression_idx: int = self.findClosingBracket(start + 1, end_statements, '(', ')')
        self.compileExpression(start + 2, closing_expression_idx - 1)
        self.addOutputLines(['not', f'if-goto WHILE_END{org_while_cnt - 1}'])
        # {statements}
        closing_statements_idx: int = self.findClosingBracket(closing_expression_idx + 1, end_statements, '{', '}')
        self.compileStatements(closing_expression_idx + 2, closing_statements_idx - 1)
        self.addOutputLines([f'goto WHILE_EXP{org_while_cnt - 1}', f'label WHILE_END{org_while_cnt - 1}'])
        return closing_statements_idx

    def compileReturn(self, start: int, end_statements: int) -> int:
        """
        'return' expression? ';'
        """
        idx: int = start
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        if idx - start > 1:  # if there is expression
            self.compileExpression(start + 1, idx - 1)
        else:  # no expression (void)
            self.addOutputLines(['push constant 0'])
        self.addOutputLines(['return'])
        return idx

    def findClosingBracket(self, start: int, end: int, open_c: str, close_c: str) -> int:
        bracket_cnt: int = 0
        idx: int = start
        while idx <= end:
            if self.token_objects[idx].token == open_c:
                bracket_cnt += 1
            elif self.token_objects[idx].token == close_c:
                bracket_cnt -= 1
                if bracket_cnt == 0:
                    return idx
            idx += 1
        print('not found')

    def compileIf(self, start, end_statements) -> int:
        """
        'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.if_cnt += 1
        org_if_cnt = self.if_cnt
        # (expression)
        closing_expression_idx: int = self.findClosingBracket(start + 1, end_statements, '(', ')')
        self.compileExpression(start + 2, closing_expression_idx - 1)
        self.addOutputLines([f'if-goto IF_TRUE{org_if_cnt - 1}',
                             f'goto IF_FALSE{org_if_cnt - 1}',
                             f'label IF_TRUE{org_if_cnt - 1}'])
        # {statements} when true
        closing_statements_idx: int = self.findClosingBracket(closing_expression_idx + 1, end_statements, '{', '}')
        self.compileStatements(closing_expression_idx + 2, closing_statements_idx - 1)
        # If no 'else'
        if (closing_statements_idx == end_statements) or (
                self.token_objects[closing_statements_idx + 1].token != 'else'):
            self.addOutputLines([f'label IF_FALSE{org_if_cnt - 1}'])
            return closing_statements_idx
        self.addOutputLines([f'goto IF_END{org_if_cnt - 1}', f'label IF_FALSE{org_if_cnt - 1}'])
        # {statements}
        closing_else_statements_idx: int = self.findClosingBracket(closing_statements_idx + 2, end_statements, '{', '}')
        self.compileStatements(closing_statements_idx + 3, closing_else_statements_idx - 1)
        self.addOutputLines([f'label IF_END{org_if_cnt - 1}'])
        return closing_else_statements_idx

    def compileExpression(self, start: int, end_exp: int) -> None:
        """
        term (op term)*
        """
        if start > end_exp:
            return
        idx: int = start
        while idx <= end_exp:
            if self.token_objects[idx].token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
                operator: str = self.token_objects[idx].token
                idx_org: int = idx
                idx = self.compileTerm(idx + 1, end_exp) + 1
                if (idx_org == start) and (operator == '-'):
                    self.addOutputLines(['neg'])
                else:
                    self.addOutputLines([f'{self.binary_operator_dic[operator]}'])
            else:
                idx = self.compileTerm(idx, end_exp) + 1

    def compileTerm(self, start: int, end_exp: int) -> None:
        """
        Cut out and compile the first term of the given expression
        """
        first_token: str = self.token_objects[start].token
        end_idx: int = start
        # One-word term
        if end_exp - start < 1:
            end_idx = end_exp
        # '(' expression ')'
        if first_token == '(':
            closing_term: int = self.findClosingBracket(start, end_exp, '(', ')')
            self.compileExpression(start + 1, closing_term - 1)
            end_idx = closing_term
        # unaryOp
        elif first_token in ['-', '~']:
            closing_right_operand: int = self.compileTerm(start + 1, end_exp)
            unary_str: str = 'neg' if first_token == '-' else 'not'
            self.addOutputLines([unary_str])
            end_idx = closing_right_operand
        # varName '[' expression ']'
        elif self.token_objects[start + 1].token == '[':
            # Process expression
            closing_term: int = self.findClosingBracket(start + 1, end_exp, '[', ']')
            self.compileExpression(start + 2, closing_term - 1)
            # Process varname
            varname: str = self.token_objects[start].token
            item: dict = self.symbol_table.refer(varname)
            # print(item)
            self.addOutputLines([f'push {item["kind_alias"]} {item["num"]}'])
            # Place the value of 'varname[expression]' to stack top
            self.addOutputLines(['add', 'pop pointer 1', 'push that 0'])
            end_idx = closing_term
        # subroutineName '(' expressionList ')'
        elif self.token_objects[start + 1].token == '(':
            closing_term: int = self.findClosingBracket(start + 1, end_exp, '(', ')')
            self.compileSubroutineCall(start, closing_term)
            end_idx = closing_term
        # (className | varName) '.' subroutineName '(' expressionList ')'
        elif self.token_objects[start + 1].token == '.':
            closing_term: int = self.findClosingBracket(start + 3, end_exp, '(', ')')
            self.compileSubroutineCall(start, closing_term)
            end_idx = closing_term
        elif self.token_objects[start].token == 'true':
            self.addOutputLines(['push constant 0', 'not'])
        elif self.token_objects[start].token == 'false':
            self.addOutputLines(['push constant 0'])
        elif self.token_objects[start].token == 'this':
            self.addOutputLines(['push pointer 0'])
        elif self.token_objects[start].token == 'null':
            self.addOutputLines(['push constant 0'])
        elif self.token_objects[start].token_type == 'IDENTIFIER':
            varname: str = self.token_objects[start].token
            item: dict = self.symbol_table.refer(varname)
            self.addOutputLines([f'push {item["kind_alias"]} {item["num"]}'])
        elif self.token_objects[start].token_type == 'STRING_CONST':
            self.compileStringConst(self.token_objects[start].token)
        elif self.token_objects[start].token_type == 'INT_CONST':
            self.addOutputLines([f'push constant {self.token_objects[start].token}'])
        return end_idx

    def compileStringConst(self, s: str):
        self.addOutputLines([f'push constant {len(s)}', 'call String.new 1'])
        for i in range(len(s)):
            self.addOutputLines([f'push constant {ord(s[i])}', 'call String.appendChar 2'])

    def addOutputLines(self, lines: 'list[str]') -> None:
        self.output_line_list.extend(lines)
        self.output_line_cnt += len(lines)
        return self.output_line_cnt

    def saveToFile(self) -> None:
        output = '\n'.join(compiler.output_line_list) + '\n'
        self.path_w = f'{self.p_file.parent}/{self.p_file.stem}.vm'
        with open(self.path_w, mode='w') as f:
            f.write(output)


if __name__ == '__main__':
    path: str = sys.argv[1]
    p_path: pathlib.Path = pathlib.Path(path)
    p_file_list: 'list[pathlib.Path]' = []
    if p_path.is_dir():
        p_file_list = list(p_path.glob('**/*.jack'))
    else:
        p_file_list = [p_path]

    symbol_table = SymbolTable()

    # for p_file in p_file_list:
    #     print(p_file)
    #     compiler = CompilationEngine(symbol_table, p_file)
    #     compiler.compile(is_first_run=True)

    # print(compiler.symbol_table.subroutine_dic)
    # print(compiler.symbol_table.class_scope)

    for p_file in p_file_list:
        print(p_file)
        compiler = CompilationEngine(symbol_table, p_file)
        compiler.compile()
        compiler.saveToFile()
