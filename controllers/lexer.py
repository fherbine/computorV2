from sly import Lexer

class BcLexer(Lexer):
    tokens = { ADD, MINUS, TIMES, DIVIDE, ASSIGN, ID, IMAG,
               LPAREN, RPAREN, LBRCK, RBRCK, MODULO, QMARK,
               COMA, NUMBER }

    ignore = ' \t'

    ADD = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    IMAG = r'[iI]'
    ID = r'[A-Za-z]+'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRCK = r'\['
    RBRCK = r'\]'
    MODULO = r'%'
    QMARK = '\?'
    COMA = r','
    NUMBER = r'(?:[0-9]*\.)?[0-9]+'

    def NUMBER(self, token):
        if float(token.value).is_integer():
            token.value = int(token.value)
        else:
            token.value = float(token.value)
        return token

    def error(self, token):
        raise SyntaxError('Unknown character `%s`' % token.value[0])
        self.index += 1
