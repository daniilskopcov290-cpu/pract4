import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.parser import parse_config
from src.errors import ConfigSyntaxError

class TestParser(unittest.TestCase):
    def test_simple_dict(self):
        config = """
        @{
            port = 8080;
            host = 'localhost';
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {
            'port': 8080,
            'host': 'localhost'
        })
    
    def test_array(self):
        config = "[1 2 3 'four']"
        result = parse_config(config)
        self.assertEqual(result, [1, 2, 3, 'four'])
    
    def test_constants(self):
        config = """
        set PORT = 8080;
        set HOST = '127.0.0.1';
        
        @{
            server_port = $PORT$;
            server_host = $HOST$;
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {
            'server_port': 8080,
            'server_host': '127.0.0.1'
        })
    
    def test_expression(self):
        config = """
        set BASE = 8000;
        set OFFSET = 80;
        
        @{
            port = $BASE + OFFSET$;
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {'port': 8080})
    
    def test_len_function(self):
        config = """
        @{
            name_length = $len('hello')$;
            items = ['a' 'b' 'c'];
            items_count = $len(items)$;
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {
            'name_length': 5,
            'items': ['a', 'b', 'c'],
            'items_count': 3
        })
    
    def test_nested_dict(self):
        config = """
        @{
            database = @{
                host = 'localhost';
                port = 5432;
            };
            cache = @{
                enabled = true;
                size = 1024;
            };
        }
        """
        result = parse_config(config)
        self.assertEqual(result['database']['host'], 'localhost')
        self.assertEqual(result['database']['port'], 5432)
    
    def test_invalid_syntax(self):
        config = "@{ port = ; }"
        with self.assertRaises(ConfigSyntaxError):
            parse_config(config)
    
    def test_comments(self):
        config = """
        /#
        Это многострочный
        комментарий
        #/
        
        @{
            key = 'value';  /# Встроенный комментарий #/
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {'key': 'value'})

if __name__ == '__main__':
    unittest.main()