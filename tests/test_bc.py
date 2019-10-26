"""Main test file for Computor V2.
"""


from controllers.lexer import BcLexer
from controllers.parser import BcParser


def get_line_result(line, **kwargs):
    if not line:
        raise ValueError('In test file line must be filled.')

    if kwargs.get('parser') and kwargs.get('lexer'):
        parser = kwargs['parser']
        lexer = kwargs['lexer']
    else:
        lexer, parser = BcLexer(), BcParser()

    return parser.parse(lexer.tokenize(line))

def bc_repl(*lines):
    lexer, parser = BcLexer(), BcParser()
    res = None

    for line in lines:
        res = get_line_result(line, lexer=lexer, parser=parser)

    return res

#=============================================================================
