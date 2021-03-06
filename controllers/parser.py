import re

from core.parser import CoreParser, _

from controllers.lexer import BcLexer
from controllers.ft_math import *
from controllers.utils import MagicStr, exit_bc, draw
from controllers.polynomial_lexparse import PolynomialInterpreter, dispatch_reduced_form
from controllers.polynomials import PolyCalc


def sanitize_result(expr):
    if isinstance(expr, float) or isinstance(expr, int):
        return int(expr) if float(expr).is_integer() else float(expr)
    return expr

class Function:
    reduced_form = {}
    complex_in_body = False
    matrix_in_body = False

    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self._body = body

    def __repr__(self):
        return 'Function(name={name}, args={args}, body={body})'.format(
            name=repr(self.name),
            args=repr(self.args),
            body=repr(self._body),
        )

    def call(self, args):
        lexer = BcLexer()
        parser = BcParser(True)

        variables = {
            str(name).upper(): value for name, value in zip(self.args, args)
        }
        parser.variables = variables

        return parser.parse(lexer.tokenize(str(self.body)))

    def simplify_body(self, value):
        simplified_body = PolynomialInterpreter(value, self.args[0])
        self.reduced_form = simplified_body.reduced_form
        return str(simplified_body)

    def _is_body_variable_in_args(self, body):
        unknown_vars = re.findall(r'[A-Za-z]+', body)

        if 'i' in unknown_vars:
            self.complex_in_body = True

        if ',' in body:
            self.matrix_in_body = True

        for var in unknown_vars:
            if (
                var.upper() not in [str(arg).upper() for arg in self.args]
                and var != 'i'
            ):
                return False

        return True

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        if isinstance(value, str) and not value:
            raise ValueError('Function\'s body is empty.')

        if not self._is_body_variable_in_args(str(value)):
            raise ValueError(
                'Var in expression must represent a defined variable or arg.'
            )

        try:
            #XXX: Try to find a proper cast to MagicStr
            value = value.to_magic_str()
        except:
            pass

        try:
            self._body = self.simplify_body(value)
        except:
            self._body = value


class BcParser(CoreParser):
    parsed_str = ''
    tokens = BcLexer.tokens

    precedence = (
        ('left', 'MINUS', 'ADD'),
        ('left', 'TIMES', 'DIVIDE', 'INTDIV', 'MODULO', 'MATRIX_TIMES'),
        ('maximum', 'LPAREN', 'RPAREN'),
        ('left', 'POWER'),
        ('left', 'IMAG'),
        ('right', 'UMINUS'),
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
        super().__init__()
        self.variables = {}
        self.functions = {}
        self.is_function_body = is_function_body

    @_('assignement',
       'get_statement',
       'eval_statement')
    def statement(self, parsed):
        return parsed[0]

    @_('expr ASSIGN expr QMARK')
    def eval_statement(self, parsed):
        if not isinstance(parsed.expr0, Function):
            raise SyntaxError('For equation first member should be a function')

        if (
            isinstance(parsed.expr1, Complex)
            or isinstance(parsed.expr1, Matrix)
        ):
            raise TypeError(
                'Cannot evaluate `{member}`.\nWrong type: {mtype}'.format(
                    member=str(parsed.expr1).replace('\n', '\\n'),
                    mtype=type(parsed.expr1).__name__,
            ))

        if not parsed[0].name.upper() in self.functions:
            raise ValueError('%s is not defined' % parsed[0].name)

        if isinstance(parsed.expr1, Complex):
            raise TypeError('Cannot evaluate function equation w/Complex.')

        function = self.functions[parsed[0].name.upper()]
        unknown = function.args[0]

        if function.complex_in_body:
            raise TypeError('Cannot evaluate function with Complex in body.')

        if function.matrix_in_body:
            raise TypeError('Cannot evaluate function with Matrix in body.')

        if isinstance(parsed.expr1, MagicStr):
            magic_str = parsed.expr1

            if str(unknown) != str(magic_str.unknown):
                raise ValueError('Unknown numbers are not compatible.')

        # else its compatible
        if not isinstance(parsed.expr1, Function):
            _tmp = Function('_tmp', [unknown], str(parsed.expr1))
            _tmp.body = str(parsed.expr1)
        else:
            if not parsed.expr1.name.upper() in self.functions:
                raise ValueError('%s is not defined' % parsed.expr1.name)

            _tmp = self.functions[parsed.expr1.name.upper()]

            if str(_tmp.args[0]) != str(unknown):
                raise ValueError('Unknown numbers are not compatible.')

        print(
            dispatch_reduced_form(function.reduced_form, function.args[0]),
            '=',
            dispatch_reduced_form(_tmp.reduced_form, _tmp.args[0]),
        )

        calc = PolyCalc()
        calc.simplify(function.reduced_form, _tmp.reduced_form)
        return '\n'.join(map(str, calc.solve()))


    @_('expr ASSIGN QMARK')
    def get_statement(self, parsed):
        if isinstance(parsed.expr, MagicStr):
            raise ValueError('%s is not defined' % parsed[0])

        if not isinstance(parsed.expr, Function):
            return parsed.expr

        if not parsed[0].name.upper() in self.functions:
            raise ValueError('%s is not defined' % parsed[0].name)

        function = self.functions[parsed[0].name.upper()]

        return str(function.body).replace(function.args[0], parsed.expr.args[0])


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
            self.functions[func.name.upper()] = func
            return func.body
        elif isinstance(parsed[0], MagicStr):
            #assign variable

            if isinstance(parsed.expr1, MagicStr):
                raise ValueError(
                    'Trying to assign undefined value to variable.'
                )

            self.variables[str(parsed[0]).upper()] = parsed[2]
            return parsed[2]

        var = re.findall('^(?![iI])[a-zA-Z]+', self.parsed_str)

        if var:
            reassign = MagicStr(var[0])
            #XXX: Hack reassign variable

            if re.match('^\s*[A-Za-z]+\s*\([A-Za-z]+\)\s*=.*', self.parsed_str):
                #XXX: Hack to reassign function
                arg = re.findall(r'\([A-Za-z]+\)', self.parsed_str)[0]
                arg = re.findall(r'[A-Za-z]+', arg)
                unknown = re.findall(r'=.*', self.parsed_str)[0]
                unknown = re.findall(r'[A-Za-z]+', unknown)

                unknown = list(set(unknown))
                unknown = [u for u in unknown if not re.match(r'[iI].*', u)]

                if [str(a) for a in arg] == [str(u) for u in unknown]:
                    func = Function(str(var[0]), arg, '')
                    func.body = parsed[2]
                    self.functions[str(var[0]).upper()] = func 
                    return func.body

            if isinstance(parsed.expr1, MagicStr):
                raise ValueError(
                    'Trying to assign undefined value to variable.'
                )

            self.variables[str(reassign).upper()] = parsed[2]
            return parsed[2]

        raise SyntaxError(f'Cannot assign {parsed[2]} to {parsed[0]}')

    # function calls
    @_('expr LPAREN expr RPAREN')
    def expr(self, parsed):
        if (
            str(parsed[0]).upper() in self.functions
            and (not isinstance(parsed.expr1, MagicStr) or (
                str(parsed.expr1).upper() in self.variables
            ))
        ):
            value = parsed[2]

            if str(parsed.expr1).upper() in self.variables :
                value = self.variables[str(parsed.expr1).upper()]

            #XXX: Do I have to support: `f(x) = ?` >> NO ?
            #Function already exists
            return self.functions[str(parsed[0]).upper()].call([value])
        else:
            #Create a new function
            #XXX: Hack for arg
            arg = re.findall(
                '^[ \t]*(?![iI])[a-zA-Z]+[ \t]*\([ \t]*(?![iI])[a-zA-Z]+[ \t]*\)',
                self.parsed_str,
            )

            if not arg:
                raise SyntaxError('Syntax error, cannot evaluate.')

            arg = re.findall('\([ \t]*[a-zA-Z]+[ \t]*\)', arg[0])

            if not arg:
                raise SyntaxError('Syntax error, cannot evaluate.')

            arg = re.findall('[a-zA-Z]+', arg[0])


            return Function(str(parsed[0]), arg, '')


    #uncompress paren / brackets for expr
    @_('LPAREN expr RPAREN',
       'LBRCK expr RBRCK')
    def expr(self, parsed):
        if isinstance(parsed.expr, MagicStr):
            new_magic_str = MagicStr('(%s)' % parsed.expr)
            new_magic_str.unknown = parsed.expr.unknown
            return new_magic_str
        return parsed.expr

    #matrix handling
    @_('expr MATRIX_TIMES expr')
    def expr(self, parsed):
        if (
            not isinstance(parsed.expr0, Matrix)
            or not isinstance(parsed.expr1, Matrix)
        ):
            return parsed.expr0 * parsed.expr1

        return parsed.expr0.matrix_mul(parsed.expr1)

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
        return parsed.matrix_elem + [parsed.expr]

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
        try:
            return parsed.expr0 * parsed.expr1
        except:
            return parsed.expr1 * parsed.expr0

    @_('expr DIVIDE expr')
    def expr(self, parsed):
        if isinstance(parsed.expr1, MagicStr):
            return parsed.expr1.__rtruediv__(parsed.expr0)

        return sanitize_result(parsed.expr0 / parsed.expr1)

    @_('expr MODULO expr')
    def expr(self, parsed):
        return parsed.expr0 % parsed.expr1

    @_('expr INTDIV expr')
    def expr(self, parsed):
        return parsed.expr0 // parsed.expr1

    @_('expr POWER expr')
    def expr(self, parsed):
        if (
            isinstance(parsed.expr1, int)
            and parsed.expr1 < 0
        ) or (
            isinstance(parsed.expr1, float)
            and not parsed.expr1.is_integer()
        ):
            raise ValueError('Power exponant must be positive integer')
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
        #XXX: Hack for arg
        arg = re.findall(
            '^[ \t]*(?![iI])[a-zA-Z]+[ \t]*\([ \t]*(?![iI])[a-zA-Z]+[ \t]*\)',
            self.parsed_str,
        )

        if arg:
            arg = re.findall('\([ \t]*[a-zA-Z]+[ \t]*\)', arg[0])
            if arg:
                arg = re.findall('[a-zA-Z]+', arg[0])[0].upper()

        arg = arg if arg else ''

        if parsed.ID.upper() in self.variables and parsed.ID.upper() != arg:
            return self.variables[parsed.ID.upper()]
        return MagicStr(parsed.ID, unknown=parsed.ID)

    @_('builtin_command')
    def statement(self, parsed):
        cmd = parsed.builtin_command
        if cmd == 'quit':
            exit_bc()
            return None
        elif cmd == 'vars':
            out = '\n'.join(
                [f'{name}: {value}' for name, value in self.variables.items()]
            )
        elif cmd == 'funcs':
            out = '\n'.join(
                [f'{f.name}({f.args[0]}): {f.body}' for f in self.functions.values()]
            )
        elif cmd == 'draw':
            filtered_funcs = {
                fname: func for fname, func in self.functions.items() if (
                    not func.matrix_in_body and not func.complex_in_body
                )
            }

            if not filtered_funcs:
                raise ValueError('There\'s nothing to dispatch')

            out = draw(filtered_funcs)
        return out

    @_('QUIT LPAREN RPAREN',
       'VARS LPAREN RPAREN',
       'DRAW LPAREN RPAREN',
       'FUNCS LPAREN RPAREN')
    def builtin_command(self, parsed):
        return parsed[0]

    def error(self, parsed):
        if parsed:
            raise SyntaxError(
                'An error occurs while parsing. Before `%s`' % parsed.value
            )
        raise SyntaxError('An error occurs while parsing.')
