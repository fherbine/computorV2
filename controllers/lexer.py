from core.lexer import CoreLexer


class BcLexer(CoreLexer):
    tokens = [ 'ADD', 'MINUS', 'MATRIX_TIMES', 'TIMES', 'INTDIV', 'DIVIDE',
               'ASSIGN', 'IMAG', 'LPAREN', 'RPAREN', 'LBRCK', 'RBRCK',
               'MODULO', 'QMARK', 'SEMICOLON', 'COMMA', 'NUMBER', 'POWER',
               'QUIT', 'VARS', 'FUNCS', 'DRAW', 'ID']

    ignore = ' \t'

    ADD = r'\+'
    MINUS = r'-'
    MATRIX_TIMES = r'\*\*'
    TIMES = r'\*'
    INTDIV = r'//'
    DIVIDE = r'/'
    ASSIGN = r'='
    QUIT = r'quit'
    VARS = r'vars'
    FUNCS = r'funcs'
    DRAW = r'draw'
    ID = r'[A-Za-z]+'
    IMAG = r'[iI]'

    LPAREN = r'\('
    RPAREN = r'\)'
    LBRCK = r'\['
    RBRCK = r'\]'
    MODULO = r'%'
    QMARK = r'\?'
    COMMA = r','
    SEMICOLON = r';'
    NUMBER = r'(?:[0-9]*\.)?[0-9]+'
    POWER = r'\^'

    def token_NUMBER(self, token):
        if float(token.value).is_integer():
            token.value = int(float(token.value))
        else:
            token.value = float(token.value)
        return token

    def token_ID(self, token):
        token.value = token.value
        return token

    def error(self, token):
        raise SyntaxError('Unknown character `%s`' % token.value[0])
        self.index += 1
