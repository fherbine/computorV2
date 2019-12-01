from sly import Lexer, Parser

from controllers.ft_math import ft_power, ft_abs

class PolyLexer(Lexer):
    tokens = { NUMBER, ADD, MINUS, TIMES, DIVIDE, LPAREN,
               RPAREN, X, POWER }


    ignore = ' \t'

    NUMBER = r'\d*\.?\d+'
    ADD = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LPAREN = r'[\(\[]'
    RPAREN = r'[\)\]]'
    I = r'[iI]'
    X = r'[A-Za-z]+(?:\^[0-9]+)?'
    POWER = r'\^'

    def NUMBER(self, token):
        if '.' in token.value:
            token.value = float(token.value)
        else:
            token.value = int(token.value)
        return token

    def X(self, token):
        value = token.value.split('^')
        power = value[-1] if len(value) == 2 else 1

        token.value = f'X^{power}'
        return token

    def I(self, token):
        raise TypeError('Complex numbers are illegal for polynomial equation.')

    def error(self, token):
        raise SyntaxError('Illegal character: `%s`' % token.value[0])
        self.index += 1


class PolyParser(Parser):
    tokens = PolyLexer.tokens

    precedence = (
        ('left', ADD, MINUS),
        ('left', X),
        ('left', TIMES, DIVIDE),
        ('left', POWER),
        ('right', UMINUS),
        ('right', UMINX)
    )

    def __init__(self):
        self.degrees = {}

    def filter_results(self):
        output = {}
        degrees = self.degrees
        for degree, times in degrees.items():
            output[degree] = sum(times)

        self.degrees = {}

        return output

    @_('xexpr')
    def statement(self, parsed):
        return self.filter_results()

    @_('expr')
    def statement(self, parsed):
        self.degrees.setdefault('X^0', [])
        self.degrees['X^0'].append(parsed.expr)

        return self.filter_results()

    @_('X')
    def statement(self, parsed):
        return {parsed.X: 1}


    @_('xexpr MINUS expr')
    def expr(self, parsed):
        return -parsed.expr

    @_('expr MINUS xexpr')
    def expr(self, parsed):
        x, coef, degree_index = parsed.xexpr
        coef = -coef
        self.degrees[x][degree_index] = coef
        return parsed.expr

    @_('xexpr ADD X',
       'X ADD xexpr')
    def xexpr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(1)
        coef, degree_index = 1, len(self.degrees[parsed.X]) - 1

        return (parsed.X, coef, degree_index)

    @_('X MINUS xexpr')
    def xexpr(self, parsed):
        x, coef, degree_index = parsed.xexpr
        coef = -coef
        self.degrees[x][degree_index] = coef
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(1)
        return (x, coef, degree_index)

    @_('xexpr MINUS X')
    def xexpr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(-1)

        return (parsed.X, -1, len(self.degrees[parsed.X]) - 1)

    @_('xexpr ADD expr',
       'expr ADD xexpr')
    def expr(self, parsed):
        """ Used if an xexpr (made of an unknown raised to the power) collide a
        `+` or a `-`. In this case, we just have to return expr"""
        return parsed.expr

    @_('expr TIMES xexpr',
       'xexpr TIMES expr')
    def xexpr(self, parsed):
        x, coef, degree_index = parsed.xexpr
        coef *= parsed.expr
        self.degrees[x][degree_index] = coef
        return (x, coef, degree_index)

    @_('xexpr DIVIDE expr')
    def xexpr(self, parsed):
        x, coef, degree_index = parsed.xexpr
        coef = coef / parsed.expr
        self.degrees[x][degree_index] = coef
        return (x, coef, degree_index)

    @_('xexpr ADD xexpr')
    def xexpr(self, parsed):
        return parsed.xexpr1

    @_('xexpr MINUS xexpr')
    def xexpr(self, parsed):
        x, coef, degree_index = parsed.xexpr1
        coef = -coef
        self.degrees[x][degree_index] = coef
        return (x, coef, degree_index)

    @_('expr TIMES X',
       'X TIMES expr')
    def xexpr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(parsed.expr)
        return (parsed.X, parsed.expr, len(self.degrees[parsed.X]) - 1)

    @_('expr DIVIDE X',
       'X DIVIDE expr')
    def xexpr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(1 / parsed.expr)
        return (parsed.X, 1 / parsed.expr, len(self.degrees[parsed.X]) - 1)

    @_('X ADD expr',
       'expr ADD X')
    def expr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(1)
        return parsed.expr

    @_('X MINUS expr',
       'expr MINUS X')
    def expr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(1)
        return -parsed.expr

    @_('X ADD X')
    def xexpr(self, parsed):
        x0, x1 = parsed.X0, parsed.X1
        self.degrees.setdefault(x0, [])
        self.degrees[x0].append(1)

        self.degrees.setdefault(x1, [])
        self.degrees[x1].append(1)
        coef1, degree_index1 = 1, len(self.degrees[x1]) - 1

        return (x1, coef1, degree_index1)

    @_('X MINUS X')
    def xexpr(self, parsed):
        x0, x1 = parsed.X0, parsed.X1
        self.degrees.setdefault(x0, [])
        self.degrees[x0].append(1)

        self.degrees.setdefault(x1, [])
        self.degrees[x1].append(-1)
        coef1, degree_index1 = -1, len(self.degrees[x1]) - 1

        return (x1, coef1, degree_index1)

    @_('MINUS X %prec UMINX')
    def xexpr(self, parsed):
        self.degrees.setdefault(parsed.X, [])
        self.degrees[parsed.X].append(-1)
        return (parsed.X, -1, len(self.degrees[parsed.X]) - 1)

    @_('expr TIMES expr')
    def expr(self, parsed):
        return parsed.expr0 * parsed.expr1

    @_('expr DIVIDE expr')
    def expr(self, parsed):
        return parsed.expr0 / parsed.expr1

    @_('expr POWER expr')
    def expr(self, parsed):
        return ft_power(parsed.expr0, parsed.expr1)

    @_('expr MINUS expr')
    def expr(self, parsed):
        return parsed.expr0 - parsed.expr1

    @_('expr ADD expr')
    def expr(self, parsed):
        return parsed.expr0 + parsed.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, parsed):
        return -parsed.expr

    @_('LPAREN expr RPAREN')
    def expr(self, parsed):
        return parsed.expr

    @_('NUMBER')
    def expr(self, parsed):
        return parsed.NUMBER

    def error(self, parsed):
        raise SyntaxError('An error occurs while parsing.')


class PolynomialInterpreter:
    _str_expr = ''
    var_name = ''
    reduced_form = {}

    def __init__(self, str_expr, var_name):
        self.str_expr = str_expr
        self.var_name = var_name
        self._get_reduced_form()

    @property
    def str_expr(self):
        return self._str_expr

    @str_expr.setter
    def str_expr(self, value):
        self._str_expr = str(value)

    def _get_reduced_form(self):
        lexer = PolyLexer()
        parser = PolyParser()

        if not self.str_expr:
            return

        self.reduced_form = parser.parse(lexer.tokenize(self.str_expr))

    def __str__(self):
        return self.dispatch()

    def dispatch(self):
        output = ''
        reduced_form = self.reduced_form

        for degree, value in reduced_form.items():
            formula = '' if not output else ' '

            if not value and (any(reduced_form.values()) or degree != 'X^0'):
                continue

            if value < 0:
                formula += '- ' if output else '-'
            else:
                formula += '+ ' if output else ''

            if degree == 'X^0':
                formula += f'{value}'
            else:
                formula += str(ft_abs(value))

                if degree == 'X^1':
                    formula += f' * {self.var_name}'
                else:
                    intdeg = degree.split('^')[-1]
                    formula += f' * {self.var_name}^{intdeg}'

            output += formula

        return f'{output}'
