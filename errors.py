class ConfigError(Exception):
    """Базовый класс ошибок конфигурации"""
    pass

class ConfigSyntaxError(ConfigError):
    """Синтаксическая ошибка"""
    pass

class ConfigEvaluationError(ConfigError):
    """Ошибка вычисления"""
    pass

class UndefinedVariableError(ConfigEvaluationError):
    """Неопределенная переменная"""
    pass