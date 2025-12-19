import json
import sys

try:
    from lark import Lark, Transformer, v_args
    from lark.exceptions import LarkError
except ImportError:
    print("Ошибка: Модуль 'lark' не установлен. Установите: pip install lark")
    sys.exit(1)

# Грамматика
GRAMMAR = r"""
start: (const_decl | dict | _NL)*

const_decl: "set" CNAME "=" value _NL
?value: number
      | string
      | array
      | dict
      | const_expr

const_expr: "$" expr "$"
?expr: add_expr
add_expr: add_expr "+" mul_expr -> add
        | mul_expr
mul_expr: func_call
        | CNAME
        | number
        | "(" expr ")"
func_call: "len" "(" (string|array|CNAME) ")"

dict: "@{" _NL? [pair (_NL pair)*] _NL? "}" _NL?
pair: CNAME "=" value ";"

array: "[" [value (WS value)*] "]" _NL?

string: "'" /[^']*/ "'"

CNAME: /[_A-Z][_a-zA-Z0-9]*/
number: SIGNED_INT

COMMENT: "/#" /(.|\n)+/ "#/"
_WS: /[ \t\f]+/          // Определяем WS
_NL: /(\r?\n)+\s*/

%ignore COMMENT
%ignore _WS
"""

class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.variables = {}
    
    def start(self, items):
        result = {}
        for item in items:
            if item is not None:
                if isinstance(item, tuple) and len(item) == 2:
                    key, value = item
                    result[key] = value
                elif isinstance(item, dict):
                    result.update(item)
        return result
    
    def const_decl(self, items):
        name = str(items[0])
        value = items[1]
        self.variables[name] = value
        return None
    
    def dict(self, items):
        result = {}
        for item in items:
            if item is not None:
                key, value = item
                result[key] = value
        return result
    
    def pair(self, items):
        key = str(items[0])
        value = items[1]
        return (key, value)
    
    def array(self, items):
        return list(items)
    
    @v_args(inline=True)
    def string(self, s):
        return str(s)
    
    @v_args(inline=True)
    def number(self, n):
        return int(n)
    
    def const_expr(self, items):
        expr_tree = items[0]
        return self._evaluate(expr_tree)
    
    def add(self, items):
        return ('add', items[0], items[1])
    
    def func_call(self, items):
        func_name = str(items[0])
        arg = items[1]
        return ('func', func_name, arg)
    
    @v_args(inline=True)
    def CNAME(self, name):
        return str(name)
    
    def _evaluate(self, node):
        if isinstance(node, tuple):
            op = node[0]
            
            if op == 'add':
                left = self._evaluate(node[1])
                right = self._evaluate(node[2])
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            
            elif op == 'func':
                func_name = node[1]
                arg = self._evaluate(node[2])
                
                if func_name == 'len':
                    if isinstance(arg, list):
                        return len(arg)
                    elif isinstance(arg, str):
                        return len(arg)
                    else:
                        raise ValueError(f"len() нельзя применить к {type(arg)}")
                else:
                    raise ValueError(f"Неизвестная функция: {func_name}")
            
            else:
                raise ValueError(f"Неизвестная операция: {op}")
        
        elif isinstance(node, str):
            if node in self.variables:
                return self.variables[node]
            else:
                raise ValueError(f"Неизвестная переменная: {node}")
        
        else:
            return node

def parse_config(text: str) -> dict:
    try:
        parser = Lark(
            GRAMMAR,
            parser='lalr',
            transformer=ConfigTransformer(),
            propagate_positions=False
        )
        
        result = parser.parse(text)
        return result
    except Exception as e:
        raise Exception(f"Ошибка парсинга: {e}")