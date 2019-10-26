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

def test_show_complex():
    assert str(get_line_result('3 + 2 * i = ?')) == '(3 + 2i)'

def test_show_implicit_complex():
    assert str(get_line_result('3 + 2i = ?')) == '(3 + 2i)'

#======================== matrix operations ==================================
#======================== composed operation =================================

def test_composed_basic_operators():
    assert get_line_result('(4/2+19) * 2 = ?') == 42

def test_composed_basic_operators_2():
    assert get_line_result('(((21%(2+20))) * 2)/1 + (0 * 42)//1 = ?') == 42

#======================== variables ==========================================

def test_simple_assignation():
    assert get_line_result('a = 42') == 42

def test_simple_assignation_with_operation():
    assert get_line_result('a = (((21%(2+20))) * 2)/1 + (0 * 42)//1') == 42

def test_simple_assignation_with_variable():
    res = bc_repl('a = 42', 'key = a')
    assert res == 42

def test_simple_assignation_with_variables_calculation():
    res = bc_repl('a = 42','one=1', 'zero = one - 1', 'key = (a + zero) * one')
    assert res == 42

def test_simple_assignation_with_func():
    res = bc_repl('a(x) = x', 'key = a(42)')
    assert res == 42

def test_simple_assignation_with_func_var_arg():
    res = bc_repl('a(x) = x * 2', 'moscow = 21', 'key = a(moscow)')
    assert res == 42

def test_simple_assignation_with_func_func_arg():
    res = bc_repl('a(x) = x * 2', 'f(x) = x', 'key = a(f(21))')
    assert res == 42

def test_complex_assignation():
    res = bc_repl(
        'a(x) = x * 2',
        'moscow = 21',
        'useless(toto) = toto',
        'two = 2',
        'key = (useless(a(moscow)) + a(0) + a(useless(moscow))) * two // 4',
    )
    assert res == 42

#======================== functions assignement ==============================
#======================== function calculation ===============================
#======================== Vars & funcs rewrite ===============================
#======================== Polynomials ========================================
#------------------------ BONUS ==============================================

def test_ask_floordiv_operation():
    assert get_line_result('85 // 2 = ?') == 42
