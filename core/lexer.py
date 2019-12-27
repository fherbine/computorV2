import re

class Token:
    token_type = ''
    value = ''

    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '{name}({attrs})'.format(
            name=type(self).__name__,
            attrs=f'type: {repr(self.token_type)}, value: {repr(self.value)}',
        )


class Tokenizer:
    def __init__(self, reg_map, text_buffer, ignore, callback_obj):
        self.reg_map = reg_map
        self.text_buffer = text_buffer
        reg = r'|'.join(reg_map.values())
        self.iterator = re.finditer(reg, text_buffer)
        self.other_matches = re.sub(reg+'|[%s]+' % ignore, '', text_buffer)
        self.callback_obj = callback_obj
        self.stop = False

    def __iter__(self):
        return self

    def __next__(self):
        callback_obj = self.callback_obj

        if self.stop:
            raise StopIteration()

        if self.other_matches:
            self.stop = True
            tok = Token('error', self.other_matches)
            tok = getattr(callback_obj, 'error')(tok)
            return tok


        it = self.iterator
        match = next(it)
        value = match.group()

        for tok_type, reg in self.reg_map.items():
            if re.match(reg, value):
                tok = Token(tok_type, value)
                tok = getattr(callback_obj, 'token_' + tok_type)(tok)
                return tok

class CoreLexer:
    """CoreLexer: Inherit from this lexer to tokenize your data.

    This class is inspired by sly lexer.

    Attributes:
        - :str: ignore = Use this attribute as a string to describe what chars
        you want to ignore.
        - :list: tokens = Use this attributes to describe the name of your
        tokens.

    Methods:
        - :iterator: tokenize(text_buffer) = It generates an iterator of tokens
        from a received string.

    """
    ignore = ''
    _regex_map = {}
    tokens = []

    def __new__(cls, *args, **kwargs):
        for token in cls.tokens:
            cls._regex_map[token] = getattr(cls, token)

        return super().__new__(cls, *args, **kwargs)

    def __getattr__(self, attr):
        """Getattr used to handle token without corresponding methods."""

        def handle_token(token):
            return token
        return handle_token

    def tokenize(self, text_buffer):
        return Tokenizer(self._regex_map, text_buffer, self.ignore, self)

    def error(self, token):
        raise SyntaxError('Error with token %s' % token)



class _TestLexer(CoreLexer):
    tokens = ['NUMBER', 'ADD', 'IS_EQUAL', 'EQUAL']
    ignore = ' \t'

    NUMBER = r'\d+'
    ADD = r'\+'
    IS_EQUAL = r'=='
    EQUAL = r'='

    def token_NUMBER(self, token):
        token.value = int(token.value)
        return token

    def error(self, token):
        raise SyntaxError('Unknown char tok %s' % token.value[0])

if __name__ == '__main__':
    lexer = _TestLexer()

    while True:
        data = input('> ')

        if data:
            try:
                print(list(lexer.tokenize(data)))
            except Exception as e:
                print(e)
