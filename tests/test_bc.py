"""Main test file for Computor V2.
"""

import re
import pytest

from controllers.lexer import BcLexer
from controllers.parser import BcParser
lexer = BcLexer()
parser = BcParser()


def get_line_result(line, **kwargs):
    if not line:
        raise ValueError('In test file line must be filled.')

    if kwargs.get('parser') and kwargs.get('lexer'):
        pars = kwargs['parser']
        lex = kwargs['lexer']
    else:
        lex = lexer
        pars = parser
        parser.variables = {}
        parser.functions = {}

    line = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', line)
    pars.parsed_str = line
    return pars.parse(lex.tokenize(line))

def bc_repl(*lines):
    res = None
    global lexer
    global parser

    parser.variables = {}
    parser.functions = {}

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

def test_show_complex_no_real_part():
    assert str(get_line_result('0 + 2 * i = ?')) == '2i'

def test_show_complex_no_imag_part():
    assert str(get_line_result('3 + 0 * i = ?')) == '3'

def test_add_complex_to_real():
    assert str(get_line_result('4 + 3 + 2 * i = ?')) == '(7 + 2i)'

def test_add_complex_expr_to_real():
    assert str(get_line_result('4 + (3 + 2 * i) = ?')) == '(7 + 2i)'

def test_add_real_to_complex():
    assert str(get_line_result('3 + 2 * i + 4= ?')) == '(7 + 2i)'

def test_add_real_expr_to_complex():
    assert str(get_line_result('(3 + 2 * i) + 4 = ?')) == '(7 + 2i)'

def test_add_complex_to_complex():
    assert str(get_line_result('(2 + 1 * i) + (4 + 2 * i) = ?')) == '(6 + 3i)'

def test_sub_complex_to_real():
    assert str(get_line_result('4 - 3 + 2 * i = ?')) == '(1 + 2i)'

def test_sub_complex_expr_to_real():
    assert str(get_line_result('4 - (3 + 2 * i) = ?')) == '(1 - 2i)'

def test_sub_real_to_complex():
    assert str(get_line_result('3 + 2 * i - 4= ?')) == '(-1 + 2i)'

def test_sub_real_expr_to_complex():
    assert str(get_line_result('(3 + 2 * i) - 4 = ?')) == '(-1 + 2i)'

def test_sub_complex_to_complex():
    assert str(get_line_result('(2 + i) - (4 + 2 * i) = ?')) == '(-2 - i)'

def test_mul_complex_to_real():
    assert str(get_line_result('4 * 3 + 2 * i = ?')) == '(12 + 2i)'

def test_mul_complex_expr_to_real():
    assert str(get_line_result('4 * (3 + 2 * i) = ?')) == '(12 + 8i)'

def test_mul_real_to_complex():
    assert str(get_line_result('3 + 2 * i * 4= ?')) == '(3 + 8i)'

def test_mul_real_expr_to_complex():
    assert str(get_line_result('(3 + 2 * i) * 4 = ?')) == '(12 + 8i)'

def test_mul_complex_to_complex():
    assert str(get_line_result('(2 + i) * (4 + 2 * i) = ?')) == '(6 + 8i)'

def test_div_complex_to_real():
    assert str(get_line_result('4 / 2 + 2 * i = ?')) == '(2 + 2i)'

def test_div_complex_expr_to_real():
    assert str(get_line_result('4 / (4 + 2 * i) = ?')) == '(0.8 - 0.4i)'

def test_div_real_to_complex():
    assert str(get_line_result('3 + 2 * i / 4= ?')) == '(3 + 0.5i)'

def test_div_real_expr_to_complex():
    assert str(get_line_result('(3 + 2 * i) / 4 = ?')) == '(0.75 + 0.5i)'

def test_div_complex_to_complex():
    assert str(get_line_result('(2 + i) / (4 + 2 * i) = ?')) == '0.5'

#======================== matrix operations ==================================

def test_get_one_dimension_matrix():
    assert str(get_line_result('[[4, 2]] = ?')) == '[4, 2]'

def test_assign_two_dimension_matrix():
    assert str(get_line_result('[[4, 2]; [2,1]] = ?')) == '[4, 2]\n[2, 1]'

def test_matrix_real_addition():
    assert str(get_line_result(
        '[[4, 2]; [2,1]] + 42 = ?'
    )) == '[46, 44]\n[44, 43]'

def test_real_matrix_addition():
    assert str(get_line_result(
        '42 + [[4, 2]; [2,1]] = ?'
    )) == '[46, 44]\n[44, 43]'

def test_matrix_real_substraction():
    assert str(get_line_result(
        '[[4, 2]; [2,1]] - 42 = ?'
    )) == '[-38, -40]\n[-40, -41]'

def test_real_matrix_substraction():
    assert str(get_line_result(
        '42 - [[4, 2]; [2,1]] = ?'
    )) == '[38, 40]\n[40, 41]'

def test_matrix_real_multiplication():
    assert str(get_line_result(
        '[[4, 2]; [2,1]] ** 2 = ?'
    )) == '[8, 4]\n[4, 2]'

def test_real_matrix_multiplication():
    assert str(get_line_result(
        '2 ** [[4, 2]; [2,1]] = ?'
    )) == '[8, 4]\n[4, 2]'

def test_matrix_real_division():
    assert str(get_line_result(
        '[[4, 2]; [2,1]] / 2 = ?'
    )) == '[2.0, 1.0]\n[1.0, 0.5]'

def test_real_matrix_division():
    assert str(get_line_result(
        '2 / [[4, 2]; [2,1]] = ?'
    )) == '[0.5, 1.0]\n[1.0, 2.0]'

def test_matrix_add_matrix():
    res = bc_repl(
        'a = [[2, 3]; [6, 7]]',
        'b = [[4, 2]; [1, 8]]',
        'a + b = ?',
    )
    assert str(res) == '[6, 5]\n[7, 15]'

def test_matrix_sub_matrix():
    res = bc_repl(
        'a = [[2, 3]; [6, 7]]',
        'b = [[4, 2]; [1, 8]]',
        'a - b = ?',
    )
    assert str(res) == '[-2, 1]\n[5, -1]'

def test_matrix_div_matrix():
    res = bc_repl(
        'a = [[2, 3]; [6, 8]]',
        'b = [[4, 2]; [1, 16]]',
        'a / b = ?',
    )
    assert str(res) == '[0.5, 1.5]\n[6.0, 0.5]'

def test_matrix_mul_matrix():
    res = bc_repl(
        'a = [[1, 0]; [2, -1]]',
        'b = [[3, 4]; [-2, -3]]',
        'a ** b = ?',
    )
    assert str(res) == '[3, 4]\n[8, 11]'

def test_matrix_mul_matrix_2():
    res = bc_repl(
        'a = [[1, 2, 0]; [4, 3, -1]]',
        'b = [[5, 1]; [2, 3]; [3, 4]]',
        'a ** b = ?',
    )
    assert str(res) == '[9, 7]\n[23, 9]'

def test_matrix_mul_matrix_3():
    res = bc_repl(
        'a = [[1, 2, 0]; [4, 3, -1]]',
        'b = [[5, 1]; [2, 3]; [3, 4]]',
        'b ** a = ?',
    )
    assert str(res) == '[9, 13, -1]\n[14, 13, -3]\n[19, 18, -4]'

#======================== composed operation =================================

def test_composed_basic_operators():
    assert get_line_result('(4/2+19) * 2 = ?') == 42

def test_composed_basic_operators_2():
    assert get_line_result('(((21%(2+20))) * 2)/1 + (0 * 42)//1 = ?') == 42

#======================== variables & funcs ==================================

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

def test_function_assignation():
    assert str(get_line_result('a(x) = 42 * x')) == '42 * x'

def test_function_assignation_reverse_factor():
    assert str(get_line_result('a(x) = x * 42')) == '42 * x'

#======================== Vars & funcs rewrite ===============================
#======================== Polynomials ========================================
ININITE = '\u221e'
NO_SOLUTION_REAL = 'There is no solution(s) in real.'
UNIQUE_SOLUTION_REAL = 'There is unique solution(s) in real.\n'
ONE_SOLUTION_REAL = 'There is one solution(s) in real.\n'
TWO_SOLUTION_REAL = 'There is two solution(s) in real.\n'
TWO_SOLUTION_COMPLEX = 'There is two solution(s) in complex.\n'
INFINITE_SOLUTION_REAL = '''There is infinite number of solution(s) in real.
''' + ININITE


def test_simple_deg0_poly_infinite():
    res = bc_repl(
        'f(x) = 0',
        'f(x) = 0 ?',
    )
    assert str(res) == INFINITE_SOLUTION_REAL

def test_simple_deg0_poly_none():
    res = bc_repl(
        'f(x) = 42',
        'f(x) = 0 ?',
    )
    assert str(res) == NO_SOLUTION_REAL

def test_simple_deg1_poly():
    res = bc_repl(
        'f(x) = x',
        'f(x) = 0 ?',
    )
    assert str(res) == UNIQUE_SOLUTION_REAL + '0'

def test_simple_deg2_poly_one_sol():
    res = bc_repl(
        'f(x) = x^2 * 2 + 9 / 8',
        'f(x) = 3 * x ?',
    )
    assert str(res) == ONE_SOLUTION_REAL + f'{3 / 4}'

def test_simple_deg2_poly_two_sol_real():
    res = bc_repl(
        'f(x) = x^2 * 2 - 6',
        'f(x) = x ?',
    )
    assert str(res) == TWO_SOLUTION_REAL + '%s\n2.0' % str(-3 / 2)

def test_simple_deg2_poly_two_sol_complex():
    res = bc_repl(
        'f(x) = x^2 + x * 4',
        'f(x) = -20 ?',
    )
    assert str(res) == TWO_SOLUTION_COMPLEX + '(-2 - 4i)\n(-2 + 4i)'

#======================== Expected errors ====================================

def test_lexer_unknown_char():
    with pytest.raises(SyntaxError):
        str(get_line_result('>'))

def test_parser_regular_syntax_error():
    with pytest.raises(SyntaxError):
        str(get_line_result('?'))

def test_negative_exp():
    with pytest.raises(ValueError):
        str(get_line_result('a = 2^-1'))

def test_float_exp():
    with pytest.raises(ValueError):
        str(get_line_result('a = 2^3.5'))

def test_variable_unknown_assignation():
    with pytest.raises(ValueError):
        str(get_line_result('a = b'))

def test_ivar_assignation():
    with pytest.raises(SyntaxError):
        str(get_line_result('i = 3'))

def test_eq_with_variable_first_member():
    with pytest.raises(SyntaxError):
        str(get_line_result('a = 0 ?'))

def test_function_assignement_wrong_var():
    with pytest.raises(ValueError):
        str(get_line_result('f(x) = y'))

def test_function_assignement_with_no_params():
    with pytest.raises(SyntaxError):
        str(get_line_result('f() = y'))

def test_equation_with_complex_right_part():
    with pytest.raises(TypeError):
        bc_repl(
            'f(x) = x',
            'f(x) = i ?'
        )

def test_equation_with_complex_left_part():
    with pytest.raises(TypeError):
        bc_repl(
            'f(x) = 2 * i',
            'f(x) = 0 ?'
        )

def test_equation_with_matrix_left_part():
    with pytest.raises(TypeError):
        bc_repl(
            'f(x) = [[2, 3]]',
            'f(x) = 0 ?'
        )

def test_equation_with_illegal_positive_degree():
    with pytest.raises(ValueError):
        bc_repl(
            'f(x) = x^3',
            'f(x) = 0 ?'
        )

def test_equation_not_compatible_unknown():
    with pytest.raises(ValueError):
        bc_repl(
            'f(x) = x',
            'f(x) = y ?'
        )

def test_equation_not_compatible_funcs_unknown():
    with pytest.raises(ValueError):
        bc_repl(
            'f(x) = x',
            'b(y) = y',
            'f(x) = b(y) ?'
        )
#============================== Subject =======================================

def test_sub_1():
    assert get_line_result('varA = 2') == 2

def test_sub_2():
    assert get_line_result('varA = 2.242') == 2.242

def test_sub_3():
    assert get_line_result('varA = -4.3') == -4.3

def test_sub_4():
    assert str(get_line_result('varA = 2*i + 3')) == '(3 + 2i)'

def test_sub_5():
    assert str(get_line_result('varA = -4i - 4')) == '(-4 - 4i)'

def test_sub_6():
    assert str(get_line_result('varA = [[2,3];[4,3]]')) == '[2, 3]\n[4, 3]'

def test_sub_7():
    assert str(get_line_result('varA = [[3,4]]')) == '[3, 4]'

def test_sub_8():
    assert str(get_line_result('funA(x) = 2*x^5 + 4x^2 - 5*x + 4')) == '2 * x^5 + 4 * x^2 - 5 * x + 4'

def test_sub_9():
    assert str(get_line_result('funB(y) = 43 * y / (4 % 2 * y)')) == '43 * y / (0 * y)'

def test_sub_10():
    assert str(get_line_result('funC(z) = -2 * z - 5')) == '-2 * z - 5'

#------------------------ BONUS ==============================================

def test_ask_floordiv_operation():
    assert get_line_result('85 // 2 = ?') == 42
