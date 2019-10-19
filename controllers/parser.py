from sly import Parser

from controllers.lexer import BcLexer
from controllers.ft_math import *

sanitize_result = lambda a: int(a) if float(a).is_integer() else float(a)

class BcParser(Parser):
    tokens = BcLexer.tokens

    precedence = (
        ('left', MINUS, ADD),
        ('left', TIMES, DIVIDE, INTDIV, MODULO),
        ('left', POWER),
        ('right', UMINUS)
    )

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

    #uncompress paren / brackets for expr
    @_('LPAREN expr RPAREN',
       'LBRCK expr RBRCK')
    def expr(self, parsed):
        return parsed.expr

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

    #UMINUS > Very high precedence
    @_('MINUS expr %prec UMINUS')
    def expr(self, parsed):
        return -parsed.expr

    # regular expr
    @_('NUMBER')
    def expr(self, parsed):
        return parsed.NUMBER

    @_('IMAG')
    def expr(self, parsed):
        return Complex(0, 1)
