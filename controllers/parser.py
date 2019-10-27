from sly import Parser

from controllers.lexer import BcLexer
from controllers.ft_math import *
from controllers.utils import MagicStr, exit_bc


def sanitize_result(expr):
    if isinstance(expr, float) or isinstance(expr, int):
        return int(expr) if float(expr).is_integer() else float(expr)
    return expr

class Function:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self._body = body

    def call(self, args):
        lexer = BcLexer()
        parser = BcParser(True)

        variables = {str(name): value for name, value in zip(self.args, args)}
        parser.variables = variables

        return parser.parse(lexer.tokenize(str(self.body)))


    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        if isinstance(value, str) and not value:
            raise ValueError('Function\'s body is empty.')

        self._body = value


class BcParser(Parser):
    tokens = BcLexer.tokens

    precedence = (
        ('left', QMARK),
        ('left', MINUS, ADD),
        ('left', TIMES, DIVIDE, INTDIV, MODULO),
        ('left', POWER),
        ('left', IMAG),
        ('right', UMINUS),
    )

    def __init__(self, is_function_body=False):
        """Define functions and variables dicts.

        self.variables struct:
        {<VAR1_CAP>: <value>, <VAR2_CAP>, ...}

        self.functions struct:
        {
            <FUNC1_CAP>: Function(),
            <FUNC2_CAP>: Function(),
            ...
        }
        """
        self.variables = {}
        self.functions = {}
        self.is_function_body = is_function_body

    @_('assignement',
       'get_statement')
    def statement(self, parsed):
        return parsed[0]

    @_('expr ASSIGN QMARK')
    def get_statement(self, parsed):
        if (
            isinstance(parsed.expr, MagicStr)
            or isinstance(parsed.expr, Function)
        ):
            raise NameError('Cannot call `%s`.' % parsed.expr)

        return parsed.expr

    @_('expr')
    def statement(self, parsed):
        if self.is_function_body:
            return parsed.expr

    @_('expr ASSIGN expr')
    def assignement(self, parsed):
        if isinstance(parsed[0], Function):
            #assign function
            func = parsed[0]
            func.body = parsed[2]
            self.functions[func.name] = func
            return func.body
        elif isinstance(parsed[0], MagicStr):
            #assign variable
            self.variables[str(parsed[0])] = parsed[2]
            return parsed[2]

        raise SyntaxError(f'Cannot assign {parsed[2]} to {parsed[0]}')

    # function calls
    @_('ID LPAREN expr RPAREN')
    def expr(self, parsed):
        if parsed[0] in self.functions:
            #Function already exists
            return self.functions[parsed[0]].call([parsed[2]])
        else:
            #Create a new function
            return Function(parsed[0], [parsed[2]], '')


    #uncompress paren / brackets for expr
    @_('LPAREN expr RPAREN',
       'LBRCK expr RBRCK')
    def expr(self, parsed):
        if isinstance(parsed.expr, MagicStr):
            return MagicStr('(%s)' % parsed.expr)
        return parsed.expr

    #matrix handling
    @_('LBRCK matrix_group RBRCK')
    def expr(self, parsed):
        return Matrix(parsed.matrix_group)

    @_('matrix_group SEMICOLON matrix')
    def matrix_group(self, parsed):
        matrix_group = parsed.matrix_group
        matrix = parsed.matrix
        matrix_group.append(matrix)
        return matrix_group

    @_('matrix')
    def matrix_group(self, parsed):
        return [parsed.matrix]

    @_('LBRCK matrix_elem RBRCK')
    def matrix(self, parsed):
        return parsed.matrix_elem

    @_('matrix_elem COMMA expr')
    def matrix_elem(self, parsed):
        return parsed.matrix_elem + expr

    @_('expr COMMA expr')
    def matrix_elem(self, parsed):
        return [parsed.expr0] + [parsed.expr1]

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

    @_('IMAG expr',
       'expr IMAG')
    def expr(self, parsed):
        return Complex(0, parsed.expr)

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
        return MagicStr(parsed.ID)

    @_('exit')
    def statement(self, _):
        exit_bc()
        return None

    @_('QUIT LPAREN RPAREN')
    def exit(self, _):
        return None
