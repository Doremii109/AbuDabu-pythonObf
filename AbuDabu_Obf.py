import ast
import random
from typing import Union

class FStr(ast.NodeTransformer):
    def form_val(self, node: ast.FormattedValue):
        _cv = {97: 'ascii', 114: 'repr', 115: 'str', -1: 'str'}
        cv = _cv[node.conversion]
        if (frmt_sp:=node.format_spec):
            return f'format({cv}({ast.unparse(node.value)}), "{ast.unparse(frmt_sp)}")'
        return f'{cv}({ast.unparse(node.value)})'
    def visit_JoinedStr(self, node):
        self.generic_visit(node)
        js_l = []
        for _node in node.values:
            if isinstance(_node, ast.FormattedValue):
                js_l.append(self.form_val(_node))
            elif isinstance(_node, ast.Constant):
                js_l.append(repr(_node.value))
        return ast.parse(f'str().join([{','.join(js_l)}])').body[0].value

np=0
def genrn() -> str:
    global np
    return '_0x'+str(abs(hash(str(np:=np+1))))

rns: list[str] = [
    genrn(),
    genrn(),
    genrn(),
    genrn(),

    genrn(),
    genrn(),
    genrn(),
    genrn(),

    genrn(),
    genrn(),
    genrn(),

    genrn(),
    genrn(),
]

def obfStr(v: str) -> str:
    key: int = random.randint(1, 255)
    enc: list[int] = [ord(c) ^ key for c in v]

    sh_ind: list[int] = list(range(len(enc)))
    random.shuffle(sh_ind)
    sh: list[int] = [enc[i] for i in sh_ind]

    unsh: list[int] = [sh_ind.index(i) for i in range(len(enc))]

    enc_co: str = ','.join(str(x) for x in sh)
    co_ind: str = ','.join(str(i) for i in unsh)

    return (
        f"(lambda {rns[0]}, {rns[1]}, {rns[2]}: ''.join("
        f"chr({rns[2]}[{rns[1]}[{rns[3]}]] ^ {rns[0]}) for {rns[3]} in range(len({rns[2]}))))("
        f"{key}, [{co_ind}], [{enc_co}])"
    )

def obfBytes(v: bytes) -> str:
    key: int = random.randint(1, 255)
    enc: list[int] = [c ^ key for c in v]

    sh_ind: list[int] = list(range(len(enc)))
    random.shuffle(sh_ind)
    sh: list[int] = [enc[i] for i in sh_ind]

    unsh: list[int] = [sh_ind.index(i) for i in range(len(enc))]

    enc_co: str = ','.join(str(x) for x in sh)
    co_ind: str = ','.join(str(i) for i in unsh)

    return (
        f"(lambda {rns[4]}, {rns[5]}, {rns[6]}: bytes("
        f"({rns[6]}[{rns[5]}[{rns[7]}]] ^ {rns[4]}) for {rns[7]} in range(len({rns[6]}))))("
        f"{key}, [{co_ind}], [{enc_co}])"
    )

def obfBool(b: bool) -> str:
    aa: str = random.choice([r'{}', '[]'])

    dict_list_gen: list[str] = [aa for _ in range(random.randint(2, 10))]
    dict_list_gen.append('[]' if aa == r'{}' else r'{}')

    sh_ind: list[int] = list(range(len(dict_list_gen)))
    random.shuffle(sh_ind)
    sh: list[int] = [dict_list_gen[i] for i in sh_ind]

    unsh: list[int] = [sh_ind.index(i) for i in range(len(dict_list_gen))]
    tuple_gen: str = f"({','.join(sh)})"
    final_tuple_gen: str = f"(lambda {rns[8]}, {rns[9]}: [{rns[9]}[{rns[8]}[{rns[10]}]] for {rns[10]} in range(len({rns[9]}))])({unsh}, {tuple_gen})"

    bool_gen: list[str] = [f"[{random.randint(1000, 9999)}][0]" for _ in range(random.randint(2, 10))]
    bool_gen.append(final_tuple_gen)
    random.shuffle(bool_gen)

    fbool: str = f'({','.join(bool_gen)})'

    if b: return f'{fbool}=={fbool}'
    else: return f'{fbool}!={fbool}'


def obfInt(i: int) -> list[str]:
    si: str = str(i)
    magic_n: int = random.randint(1000000, 9999999)
    enc_i: list[str] = []
    for char in si:
        int_: int = int(char)
        op_index: int = random.randint(1, 6)
        if op_index == 1:
            op: str = '+'
            key: int = int_ - magic_n
        elif op_index == 2:
            op: str = '-'
            key: int = int_ + magic_n
        elif op_index == 3:
            op: str = r'/'
            key: int = int_ * magic_n
        elif op_index == 4:
            op: str = '*'
            key: int = int_ / magic_n
        elif op_index == 5:
            op: str = '^'
            key: int = int_ ^ magic_n
        elif op_index == 6:
            magic_n: int = random.randint(1, 19)
            op: str = '>>'
            key: int = int_ << magic_n
        
        enc_i.append(f'(lambda {rns[11]}, {rns[12]}: str(int({rns[12]} {op} {rns[11]})))({magic_n}, {key})')

    return enc_i


class CO(ast.NodeTransformer):
    def __init__(self) -> None:
        self.class_name: str = genrn()
        self.consts: dict = {}
        self.value_to_alias: dict = {}

    def visit_Constant(self, node: ast.Constant) -> ast.Attribute:
        if node.value in self.value_to_alias: alias_name = self.value_to_alias[node.value]
        else:
            alias_name = genrn()
            self.consts[alias_name] = node.value
            self.value_to_alias[node.value] = alias_name
        
        return ast.Attribute(value=ast.Name(id=self.class_name, ctx=ast.Load()), attr=alias_name, ctx=ast.Load())

    def cCD(self, tree: ast.Module) -> ast.Module:
        class_body = []
        for alias, value in self.consts.items():
            assign = ast.Assign(targets=[ast.Name(id=alias, ctx=ast.Store())], value=ast.Constant(value=value), lineno=0)
            class_body.append(assign)

        class_def = ast.ClassDef(name=self.class_name, bases=[], keywords=[], body=class_body, decorator_list=[], lineno=0)

        tree.body.insert(0, class_def)
        return tree


class strObf(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, (str, bytes)):
            BYTES: bool = False
            if isinstance(node.value, str):
                BYTES: bool = False
                if node.value == '': return node
            else:
                BYTES: bool = True
                if node.value == b'': return node

            n: int = random.randint(1, len(node.value)-(len(node.value)//4))
            p: list[Union[str, bytes]] = [node.value[i:i+n] for i in range(0, len(node.value), n)]
            op: list[Union[str, bytes]] = [(obfBytes(x) if BYTES else obfStr(x)) for x in p]

            if BYTES:
                node: ast.Call = ast.Call(func=ast.Name(id="bytes([]).join", ctx=ast.Load()), args=[ast.List(elts=[ast.Name(id=hui, ctx=ast.Load()) for hui in op], ctx=ast.Load())], keywords=[])
            else:
                node: ast.Call = ast.Call(func=ast.Name(id="str().join", ctx=ast.Load()), args=[ast.List(elts=[ast.Name(id=hui, ctx=ast.Load()) for hui in op], ctx=ast.Load())], keywords=[],)
            return node
        
        elif isinstance(node.value, bool):
            ebu: str = obfBool(node.value)
            node: ast.Name = ast.Name(id=ebu, ctx=ast.Load())
            return node
        
        elif isinstance(node.value, float): return node

        elif isinstance(node.value, int):
            enc_i: str = obfInt(node.value)
            node: ast.Call = ast.Call(func=ast.Name(id='int', ctx=ast.Load()), args=[ast.Call(func=ast.Name(id='str().join', ctx=ast.Load()), args=[ast.List(elts=[ast.Name(id=hui, ctx=ast.Load()) for hui in enc_i], ctx=ast.Load())], keywords=[])], keywords=[])
            return node

        return self.generic_visit(node)


banner: str = r'''      __        __        __       
 /\  |__) |  | |  \  /\  |__) |  | 
/~~\ |__) \__/ |__/ /~~\ |__) \__/ 
 __   __   ___       __   __       ___  __   __  
/  \ |__) |__  |  | /__` /  `  /\   |  /  \ |__) 
\__/ |__) |    \__/ .__/ \__, /~~\  |  \__/ |  \ 

by Doremi109 or @pyexec
channel https://t.me/doratools_channel
GitHub: https://github.com/Doremii109/AbuDabu-pythonObf
'''

print(banner)

__file__: str = input('Enter file: ')
tree: ast.Module = ast.parse(open(__file__, 'r', encoding='utf8', errors='ignore').read())

_code: ast.Module = JSF().visit(tree)
co: CO = CO()
_code: ast.Module = co.cCD(co.visit(_code))
_code: str = ast.unparse(strObf().visit(_code))

file_name = __file__[:-3]+'-obf.py'
print('File obfuscated, name:', file_name)
open(file_name, 'w', encoding='utf8', errors='ignore').write(_code)
