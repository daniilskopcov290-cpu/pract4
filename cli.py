#!/usr/bin/env python3
import argparse
import sys
import json
import re

def parse_config_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return parse_config(content)

def parse_config(content):
    variables = {}
    result = {}
    
    # Удаляем комментарии
    content = re.sub(r'/#.*?#/', '', content, flags=re.DOTALL)
    
    # Парсим константы
    for match in re.finditer(r'set\s+(\w+)\s*=\s*(.+?);', content, re.DOTALL):
        name = match.group(1)
        value_str = match.group(2).strip()
        variables[name] = parse_value(value_str, variables)
    
    # Парсим словари
    dict_match = re.search(r'@\{(.*?)\}', content, re.DOTALL)
    if dict_match:
        dict_content = dict_match.group(1)
        pairs = [p.strip() for p in dict_content.split(';') if p.strip()]
        
        for pair in pairs:
            if '=' in pair:
                key, value_str = pair.split('=', 1)
                key = key.strip()
                value_str = value_str.strip()
                result[key] = parse_value(value_str, variables)
    
    return result

def parse_value(value_str, variables):
    value_str = value_str.strip()
    
    # Строка
    if value_str.startswith("'") and value_str.endswith("'"):
        return value_str[1:-1]
    
    # Число
    if re.match(r'^[+-]?\d+$', value_str):
        return int(value_str)
    
    # Массив
    if value_str.startswith('[') and value_str.endswith(']'):
        items = value_str[1:-1].strip().split()
        return [parse_value(item, variables) for item in items if item]
    
    # Выражение
    if value_str.startswith('$') and value_str.endswith('$'):
        expr = value_str[1:-1].strip()
        
        # Сложение
        if '+' in expr:
            parts = expr.split('+')
            total = 0
            for part in parts:
                part = part.strip()
                val = parse_value(part, variables)
                if isinstance(val, int):
                    total += val
                else:
                    try:
                        total += int(val)
                    except:
                        pass
            return total
        
        # len()
        if expr.startswith('len('):
            arg = expr[4:-1].strip()
            val = parse_value(arg, variables)
            if isinstance(val, (list, str)):
                return len(val)
            return 0
        
        # Простая переменная
        return parse_value(expr, variables)
    
    # Переменная
    if value_str in variables:
        return variables[value_str]
    
    return value_str

def main():
    parser = argparse.ArgumentParser(description='Конвертер конфигурации в JSON')
    parser.add_argument('input', help='Входной файл')
    
    args = parser.parse_args()
    
    try:
        result = parse_config_file(args.input)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()