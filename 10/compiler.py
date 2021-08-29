import pathlib
import sys
from tokenizer import TokenObject, JackTokenizer


class CompilationEngine:
    def __init__(self, token_objects: 'list[TokenObject]', p_file: str) -> None:
        self.token_objects = token_objects
        self.p_file = p_file
        self.statement_keyword_dic = {
            'let': self.compileLet,
            'if': self.compileIf,
            'while': self.compileWhile,
            'do': self.compileDo,
            'return': self.compileReturn}
        self.output = ''
        pass

    def compile(self):
        print(len(self.token_objects) - 1)
        self.compileClasses(0, len(self.token_objects) - 1)

    def compileClasses(self, start: int, end_script: int):
        if start >= end_script:
            return
        closing_class_idx = self.compileClass(start, end_script)
        print(self.token_objects[closing_class_idx].token)
        return self.compileClasses(closing_class_idx + 1, end_script)

    def compileClass(self, start: int, end_script: int):
        """
        'class' className '{' classVarDec* subroutineDec* '}'
        ex) class Bar {...}
        """
        self.token_objects[start].before.append('<class>')
        print(self.token_objects[start + 1].token)
        closing_class_body_idx: int = self.findClosingBracket(start + 2, end_script, '{', '}')
        self.compileClassBody(start + 3, closing_class_body_idx - 1)
        self.token_objects[closing_class_body_idx].after.append('</class>')
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
        self.token_objects[start].before.append('<classVarDec>')
        print(self.token_objects[start + 1].token)
        idx: int = start
        while idx <= end_class_body:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.token_objects[idx].after.append('</classVarDec>')
        return idx

    def compileSubroutineDec(self, start: int, end_class_body: int) -> int:
        """
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' '{' subroutineBody '}'
        ex) 'method int hoge (...) {...}'
        """
        self.token_objects[start].before.append('<subroutineDec>')
        print(self.token_objects[start + 2].token)
        closing_param_list_idx: int = self.findClosingBracket(start + 3, end_class_body, '(', ')')
        self.compileParameterList(start + 4, closing_param_list_idx - 1)
        self.token_objects[closing_param_list_idx + 1].before.append('<subroutineBody>')
        closing_subr_body_idx: int = self.findClosingBracket(closing_param_list_idx + 1, end_class_body, '{', '}')
        self.token_objects[closing_subr_body_idx].after.append('</subroutineBody>')
        self.compileSubroutineBody(closing_param_list_idx + 2, closing_subr_body_idx - 1)
        self.token_objects[closing_subr_body_idx].after.append('</subroutineDec>')
        return closing_subr_body_idx

    def compileSubroutineBody(self, start: int, end_body: int) -> None:
        """
        varDec* statements
        ex) 'var int a; let a = 1; return a;'
        """
        if start >= end_body:
            return
        first_token: str = self.token_objects[start].token
        if first_token == 'var':
            end_idx: int = self.compileVarDec(start, end_body)
            return self.compileSubroutineBody(end_idx + 1, end_body)
        else:
            self.token_objects[start].before.append('<statements>')
            end_idx: int = self.compileStatements(start, end_body)
            self.token_objects[end_body].after.append('</statements>')
            return

    def compileSubroutineCall(self, start: int, end: int) -> None:
        """
        subroutineName '(' expressionList ')' |
        (className | varName) '.' subroutineName '(' expressionList ')'
        ex) 'run()', 'a.run()'
        """
        # self.token_objects[start].before.append('<term>')
        idx: int = start
        while self.token_objects[idx].token != '(':
            idx += 1
        self.token_objects[idx].after.append('<expressionList>')
        closing_expression_list = self.findClosingBracket(idx, end, '(', ')')
        self.compileExpressionList(idx + 1, closing_expression_list - 1)
        self.token_objects[closing_expression_list].before.append('</expressionList>')
        # self.token_objects[end].after.append('</term>')

    def compileExpressionList(self, start: int, end: int) -> None:
        if start > end:
            return
        idx: int = start
        exp_start_idx: int = start
        while idx <= end:
            if self.token_objects[idx].token == ',':
                self.compileExpression(exp_start_idx, idx - 1)
                exp_start_idx = idx + 1
            idx += 1
        self.compileExpression(exp_start_idx, end)

    def compileParameterList(self, start: int, end: int):
        """
        ((type varName) (',' type varName)*)?
        ex) 'int a, char c', ''
        """
        if start > end:
            self.token_objects[end].after.append('<parameterList>')
            self.token_objects[start].before.append('</parameterList>')
        else:
            self.token_objects[start].before.append('<parameterList>')
            self.token_objects[end].after.append('</parameterList>')

    def compileVarDec(self, start: int, end_body: int) -> int:
        """
        'var' type varName (',' varname)* ';'
        ex) 'int a, b;';
        """
        self.token_objects[start].before.append('<varDec>')
        idx: int = start
        while idx <= end_body:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.token_objects[idx].after.append('</varDec>')
        return idx

    def compileStatements(self, start: int, end_statements: int) -> None:
        if start >= end_statements:
            return
        first_token: str = self.token_objects[start].token
        end_statement: int = self.statement_keyword_dic[first_token](start, end_statements)
        self.compileStatements(end_statement + 1, end_statements)

    def compileDo(self, start: int, end_statements: int) -> int:
        """
        'do' subroutineCall ';'
        """
        self.token_objects[start].before.append('<doStatement>')
        idx: int = start
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.token_objects[idx].after.append('</doStatement>')
        self.compileSubroutineCall(start + 1, idx - 1)
        return idx

    def compileLet(self, start: int, end_statements: int) -> int:
        """
        'let' varname ('[' expression ']')? '=' expression ';'
        """
        self.token_objects[start].before.append('<letStatement>')
        right_operand_start_idx: int = None
        if self.token_objects[start + 2].token == '[':
            closing_expression_idx: int = self.findClosingBracket(start + 2, end_statements, '[', ']')
            self.compileExpression(start + 3, closing_expression_idx - 1)
            right_operand_start_idx = closing_expression_idx + 2
        else:
            right_operand_start_idx = start + 3
        idx: int = right_operand_start_idx
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.token_objects[idx].after.append('</letStatement>')
        self.compileExpression(right_operand_start_idx, idx - 1)
        return idx

    def compileWhile(self, start: int, end_statements: int) -> int:
        """
        'while' '(' expression ')' '{' statements '}'
        """
        self.token_objects[start].before.append('<whileStatement>')
        # (expression)
        closing_expression_idx: int = self.findClosingBracket(start + 1, end_statements, '(', ')')
        self.compileExpression(start + 2, closing_expression_idx - 1)
        # {statements}
        closing_statements_idx: int = self.findClosingBracket(closing_expression_idx + 1, end_statements, '{', '}')
        self.token_objects[closing_expression_idx + 2].before.append('<statements>')
        self.compileStatements(closing_expression_idx + 2, closing_statements_idx - 1)
        self.token_objects[closing_statements_idx - 1].after.append('</statements>')
        self.token_objects[closing_statements_idx].after.append('</whileStatement>')
        return closing_statements_idx

    def compileReturn(self, start: int, end_statements: int) -> int:
        """
        'return' expression? ';'
        """
        self.token_objects[start].before.append('<returnStatement>')
        idx: int = start
        while idx <= end_statements:
            if self.token_objects[idx].token == ';':
                break
            idx += 1
        self.token_objects[idx].after.append('</returnStatement>')
        if idx - start > 1:
            self.compileExpression(start + 1, idx - 1)
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
        self.token_objects[start].before.append('<ifStatement>')
        # (expression)
        closing_expression_idx: int = self.findClosingBracket(start + 1, end_statements, '(', ')')
        self.compileExpression(start + 2, closing_expression_idx - 1)
        # {statements}
        closing_statements_idx: int = self.findClosingBracket(closing_expression_idx + 1, end_statements, '{', '}')
        self.token_objects[closing_expression_idx + 2].before.append('<statements>')
        self.compileStatements(closing_expression_idx + 2, closing_statements_idx - 1)
        self.token_objects[closing_statements_idx - 1].after.append('</statements>')
        # else
        if (closing_statements_idx == end_statements) or (
                self.token_objects[closing_statements_idx + 1].token != 'else'):
            self.token_objects[closing_statements_idx].after.append('</ifStatement>')
            return closing_statements_idx
        # {statements}
        closing_else_statements_idx: int = self.findClosingBracket(closing_statements_idx + 2, end_statements, '{', '}')
        self.token_objects[closing_statements_idx + 3].before.append('<statements>')
        self.compileStatements(closing_statements_idx + 3, closing_else_statements_idx - 1)
        self.token_objects[closing_else_statements_idx - 1].after.append('</statements>')
        self.token_objects[closing_else_statements_idx].after.append('</ifStatement>')
        return closing_else_statements_idx

    def compileExpression(self, start: int, end_exp: int) -> None:
        """
        term (op term)*
        """
        self.token_objects[start].before.append('<expression>')
        if start > end_exp:
            return
        idx: int = start
        while idx <= end_exp:
            # print(idx, end_exp)
            idx = self.compileTerm(idx, end_exp)
            idx += 1
            if self.token_objects[idx].token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
               idx += 1 
        self.token_objects[end_exp].after.append('</expression>')

    def compileTerm(self, start: int, end_exp: int) -> None:
        self.token_objects[start].before.append('<term>')
        first_token: str = self.token_objects[start].token
        print(first_token)
        end_idx: int = start
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
            end_idx = closing_right_operand
        # varName '[' expression ']'
        elif self.token_objects[start + 1].token == '[':
            closing_term: int = self.findClosingBracket(start, end_exp, '[', ']')
            self.compileExpression(start + 2, closing_term - 1)
            end_idx = closing_term
        # subroutineName '(' expressionList ')'
        elif self.token_objects[start + 1].token == '(':
            print('subroutine')
            closing_term: int = self.findClosingBracket(start + 1, end_exp, '(', ')')
            self.compileSubroutineCall(start, closing_term)
            end_idx = closing_term
        # (className | varName) '.' subroutineName '(' expressionList ')'
        elif self.token_objects[start + 1].token == '.':
            print('subroutine')
            closing_term: int = self.findClosingBracket(start + 3, end_exp, '(', ')')
            self.compileSubroutineCall(start, closing_term)
            end_idx = closing_term
        self.token_objects[end_idx].after.append('</term>')
        return end_idx

    def saveToFile(self) -> None:
        self.output += '\n'.join([token_object.format() for token_object in self.token_objects]) + '\n'
        self.path_w = f'{self.p_file.parent}/{self.p_file.stem}.xml'
        with open(self.path_w, mode='w') as f:
            f.write(self.output)


if __name__ == '__main__':
    path: str = sys.argv[1]
    p_path: pathlib.Path = pathlib.Path(path)
    p_file_list: 'list[pathlib.Path]' = []
    if p_path.is_dir():
        p_file_list = list(p_path.glob('**/*.jack'))
    else:
        p_file_list = [p_path]

    for p_file in p_file_list:
        print(p_file)
        tokenizer = JackTokenizer(p_file)
        while tokenizer.hasMoreLine():
            tokenizer.advance()
        compiler = CompilationEngine(tokenizer.token_objects, p_file)
        compiler.compile()
        compiler.saveToFile()
