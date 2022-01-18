import BuiltInSubroutineDic


class SymbolTable:
    def __init__(self) -> None:
        self.class_scope = self.subroutine_scope = {}
        self.subroutine_dic = BuiltInSubroutineDic.functions
        # self.subroutine_dic = {}
        self.static_num = self.field_num = self.arg_num = self.local_num = 0

    def clearClassScope(self) -> None:
        self.field_num = self.static_num = 0
        self.class_scope = {}

    def clearSubroutineScope(self) -> None:
        self.local_num = self.arg_num = 0
        self.subroutine_scope = {}

    def createItem(self, name: str, type: str, kind: str, num: int) -> dict:
        kind_alias_dic = {
            'STATIC': 'static',
            'FIELD': 'this',
            'ARG': 'argument',
            'VAR': 'local'
        }
        return {
            'name': name,
            'type': type,  # int, boolean, char
            'kind': kind,  # STATIC, FIELD, ARG, VAR
            'kind_alias': kind_alias_dic[kind],
            'num': num
        }

    def createSubroutineItem(self, type: str, kind: str) -> dict:
        return {'type': type,  # int, boolean, char
                'kind': kind}  # method, function, constructor

    def define(self, name: str, type: str, kind: str) -> dict:
        num: int = None
        item: dict = None
        if len(kind) != 3:
            if kind == 'STATIC':
                num = self.static_num
                self.static_num += 1
            else:  # FIELD
                num = self.field_num
                self.field_num += 1
            item = self.createItem(name, type, kind, num)
            self.class_scope[name] = item
            print('defined', 'class_scope', name, type, kind, num)
        else:
            if kind == 'ARG':
                num = self.arg_num
                self.arg_num += 1
            else:  # VAR
                num = self.local_num
                self.local_num += 1
            item = self.createItem(name, type, kind, num)
            self.subroutine_scope[name] = item
            # print('defined', 'subroutine_scope', name, type, kind, num)
        return item


    def refer(self, name):
        item: dict = None
        if name in self.subroutine_scope.keys():
            item = self.subroutine_scope[name]
            # print('used', 'subroutine_scope', item['name'], item['type'], item['kind'], item['num'])
            return item
        if name in self.class_scope.keys():
            item = self.class_scope[name]
            # print('used', 'class_scope', item['name'], item['type'], item['kind'], item['num'])
            return item
        raise(Exception(name, 'is Not defined'))

    def defineSubroutine(self, class_name: str, name: str, type: str, kind: str) -> dict:
        item: dict = self.createSubroutineItem(type, kind)
        if class_name in self.subroutine_dic.keys():
            self.subroutine_dic[class_name][name] = item
        else:
            self.subroutine_dic[class_name] = {}
            self.subroutine_dic[class_name][name] = item
        return item

    def referSubroutine(self, class_name: str, name: str) -> dict:
        if class_name in self.subroutine_dic.keys():
            dic: dict = self.subroutine_dic[class_name]
            if name in dic.keys():
                return dic[name]
        raise(Exception(name, 'is Not defined'))
