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
        ('right', UMINUS),
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

    @_('ID ASSIGN QMARK')
    def statement(self, parsed):
        print(self.variables[parsed.ID])

    @_('ID ASSIGN expr')
    def statement(self, parsed):
        self.variables[parsed.ID] = parsed.expr
        return parsed.expr

    # getting func arg
    @_('ID LPAREN ID RPAREN')
    def function(self, parsed):
        return 'func %s' % parsed[2]

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

    # calling ID (var/func)
    @_('ID')
    def expr(self, parsed):
        if parsed.ID in self.variables:
            return self.variables[parsed.ID]
        return 0
