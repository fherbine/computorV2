from sly import Parser

from controllers.lexer import BcLexer
from controllers.ft_math import *

sanitize_result = lambda a: int(a) if float(a).is_integer() else float(a)

class BcParser(Parser):
    tokens = BcLexer.tokens

    def __init__(self):
        """Define functions and variables dicts.

        self.variables struct:
        {<VAR1_CAP>: <value>, <VAR2_CAP>, ...}

        self.functions struct:
        {
            <FUNC1_CAP>: BcFunc(),
            <FUNC2_CAP>: BcFunc(),
            ...
        }
        """
        self.variables = {}
        self.functions = {}

    # regular expr operations
    @_('expr ADD expr')
    def expr(self, parsed):
        return parsed.expr0 + parsed.expr1

    @_('expr MINUS expr')
    def expr(self, parsed):
        return parsed.expr0 - parsed.expr1

    @_('expr TIMES expr')
    def expr(self, parsed):
        return parsed.expr0 * parsed.expr1

    @_('expr DIVIDE expr')
    def expr(self, parsed):
        return sanitize_result(parsed.expr0 / parsed.expr1)

    @_('expr MODULO expr')
    def expr(self, parsed):
        return parsed.expr0 % parsed.expr1

    @_('expr INTDIV expr')
    def expr(self, parsed):
        return parsed.expr0 // parsed.expr1

    @_('expr POWER expr')
    def expr(self, parsed):
        return ft_power(parsed.expr0, parsed.expr1)

    # regular expr
    @_('NUMBER')
    def expr(self, parsed):
        return parsed.NUMBER

    @_('IMAG')
    def expr(self, parsed):
        return Complex(0, 1)
