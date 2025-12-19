class Evaluator:
    def __init__(self, variables):
        self.variables = variables
    
    def evaluate(self, node):
        """Рекурсивное вычисление выражения"""
        if isinstance(node, tuple):
            op = node[0]
            
            if op == 'add':
                left = self.evaluate(node[1])
                right = self.evaluate(node[2])
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            
            elif op == 'func':
                func_name = node[1]
                arg = self.evaluate(node[2])
                
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
            # Это имя переменной
            if node in self.variables:
                return self.variables[node]
            else:
                raise ValueError(f"Неизвестная переменная: {node}")
        
        else:
            # Это число или строка
            return node