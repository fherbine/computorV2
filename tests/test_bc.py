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


#======================= basic math calcultaion ==============================

def test_ask_number():
    assert get_line_result('42 = ?') == 42

def test_ask_add_operation():
    assert get_line_result('21 + 21 = ?') == 42

def test_ask_sub_operation():
    assert get_line_result('63 - 21 = ?') == 42

def test_ask_mul_operation():
    assert get_line_result('2 * 21 = ?') == 42

def test_ask_truediv_operation():
    assert get_line_result('84 / 2 = ?') == 42

def test_ask_mod_operation():
    assert get_line_result('42 % 101 = ?') == 42

#======================== complex operations =================================
#======================== matrix operations ==================================
#======================== composed operation =================================

def test_composed_basic_operators():
    assert get_line_result('(4/2+19) * 2 = ?') == 42

def test_composed_basic_operators_2():
    assert get_line_result('(((21%(2+20))) * 2)/1 + (0 * 42)//1 = ?') == 42

#======================== variable assignement ===============================
#======================== variable calculation ===============================
#======================== functions assignement ==============================
#======================== function calculation ===============================
#======================== Polynomials ========================================
#------------------------ BONUS ==============================================

def test_ask_floordiv_operation():
    assert get_line_result('85 // 2 = ?') == 42
