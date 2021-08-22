import re
import pathlib
import sys
import tokenDic


class TokenObject:
    def __init__(self, token, token_type) -> None:
        self.token = token
        self.token_type = token_type

    def format(self) -> str:
        substitute_symbol_dic: str[str] = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
        temp_token: str = self.token
        if self.token in substitute_symbol_dic.keys():
            temp_token = substitute_symbol_dic[self.token]
        substitute_type_dic: str[str] = {'string_const': 'stringConstant', 'int_const': 'integerConstant'}
        temp_token_type = self.token_type.lower()
        if temp_token_type in substitute_type_dic.keys():
            temp_token_type = substitute_type_dic[temp_token_type]
        return f'<{temp_token_type}> {temp_token} </{temp_token_type}>'


class JackTokenizer:
    def __init__(self, p_file: str) -> None:
        self.p_file = p_file
        with open(p_file) as f:
            s: str = f.read()
        s = re.sub(r'(//.*\n|/\*.(.|\s)*?\*/)', '\n', s)  # delete comments
        s = re.sub(r' *\n', '\n', s)  # delete spaces at the end of lines
        self.lines: list[str] = s.split('\n')
        self.lines = [line for line in self.lines if not re.match(r'^\s*$', line)]
        self.current_line_num: int = 0
        self.line_num: int = len(self.lines)
        self.output: str = '<tokens>\n'

    def tokenizeLine(self, line: str) -> 'list[TokenObject]':
        token_objects: list[TokenObject] = []
        token: str = ''
        token_type: str = ''
        len_of_word: int = len(line)
        idx: int = 0
        beg_idx: int = 0
        while idx < len_of_word:
            if line[idx] == '"':
                beg_idx = idx + 1
                idx += 1
                while idx < len_of_word:
                    if line[idx] == '"':
                        token_objects.append(TokenObject(line[beg_idx:idx], 'STRING_CONST'))
                        beg_idx = idx + 1
                        break
                    idx += 1
            elif line[idx] in tokenDic.symbols:
                if beg_idx != idx:
                    token = line[beg_idx:idx]
                    token_type = self.tokenType(token)
                    token_objects.append(TokenObject(token, token_type))
                token_objects.append(TokenObject(line[idx], 'SYMBOL'))
                beg_idx = idx + 1
            elif line[idx] == ' ' or line[idx] == '\t':
                if beg_idx != idx:
                    token = line[beg_idx:idx]
                    token_type = self.tokenType(token)
                    token_objects.append(TokenObject(token, token_type))
                beg_idx = idx + 1
            idx += 1
        return token_objects

    def tokenType(self, token) -> str:
        """
        Determine the type of a given token
        """
        if token in tokenDic.keywords:
            return 'KEYWORD'
        elif token in tokenDic.symbols:
            return 'SYMBOL'
        elif token.isdecimal():
            if int(token) <= 32767:
                return 'INT_CONST'
            else:
                SyntaxError('Value more than 32767 is not accepted')
        else:
            if token[0].isdecimal():
                SyntaxError('Identifier starts with a number is not accepted')
            else:
                return 'IDENTIFIER'

    def hasMoreLine(self) -> bool:
        return True if self.current_line_num < self.line_num else False

    def advance(self) -> bool:
        print(self.current_line_num)
        line = self.lines[self.current_line_num]
        token_objects = self.tokenizeLine(line)
        self.output += '\n'.join([token_object.format() for token_object in token_objects]) + '\n'
        self.current_line_num += 1

    def saveToFile(self) -> None:
        self.output += '</tokens>\n'
        self.path_w = f'{self.p_file.parent}/{self.p_file.stem}T.xml'
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
        # print(p_file)
        tokenizer = JackTokenizer(p_file)
        while tokenizer.hasMoreLine():
            tokenizer.advance()
        tokenizer.saveToFile()
