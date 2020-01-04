"""Own math module.

Contained functions are:
- ft_abs(n): return the absolute value of n.
- ft_power(n, p): return n raised to power p
- ft_sqrt(n): return the square root of n. Should be improved !

Contained objects are:
- Complex(r, i): Represents a coplex number.
"""

import operator

from controllers.utils import MagicStr


def ft_abs(n):
    return -n if n < 0 else n


def ft_power(n, p):
    total = 1

    if isinstance(n, MagicStr) or isinstance(p, MagicStr):
        return(MagicStr(f'{n}^{p}'))

    if isinstance(p, Complex):
        raise TypeError('Complex power is not handled.')

    if p < 0:
        raise ValueError('power must be positive integer.')

    for _ in range(p):
        total *= n

    return total


def ft_sqrt(n):
    if n < 0:
        raise ValueError('Square root function is not defined for negatives.')
    i = 0

    # Ugly way to calculate sqrt :/

    while (i+1) * (i+1) <= n:
        i += 1

    while (i+.1) * (i+.1) <= n:
        i+= .1

    while (i+.01) * (i+.01) <= n:
        i += .01

    while (i+.001) * (i+.001) <= n:
        i += .001

    while (i+.0001) * (i+.0001) <= n:
        i += .0001

    return i


class Complex:
    def __init__(self, r, i):
        self._r = r
        self._i = i

    @property
    def r(self):
        if not isinstance(self._r, int):
            return int(self._r) if self._r.is_integer() else self._r
        return self._r

    @r.setter
    def r(self, value):
        self._r = value

    @property
    def i(self):
        if not isinstance(self._i, int):
            return int(self._i) if self._i.is_integer() else self._i
        return self._i

    @i.setter
    def i(self, value):
        self._i = value

    def __repr__(self):
        return "'%s'" % self.__str__()

    def __str__(self):
        r, i = self.r, self.i
        separator = '+' if i >= 0 else '-'
        i = ft_abs(i)

        if not i:
            return f'{r}'

        if i == 1:
            i = ''

        if not r:
            if separator == '+':
                separator = ''

            return f'{separator}{i}i'

        return f'({r} {separator} {i}i)'

    def __add__(self, number):
        if isinstance(number, MagicStr):
            return number.__radd__(self)

        r = self.r
        i = self.i

        if isinstance(number, Complex):
            r = self.r + number.r
            i = self.i + number.i
            return Complex(r, i)
        return Complex(r + number, i)

    def __radd__(self, number):
        return self.__add__(number)

    def __sub__(self, number):
        if isinstance(number, MagicStr):
            return number.__rsub__(self)

        r = self.r
        i = self.i

        if isinstance(number, Complex):
            r = self.r - number.r
            i = self.i - number.i
            return Complex(r, i)
        return Complex(r - number, i)

    def __rsub__(self, number):
        r = self.r
        i = self.i

        return Complex(number, 0) - self

    def __mul__(self, number):
        if isinstance(number, Complex):
            r = self.r * number.r - self.i * number.i
            i = self.r * number.i + number.r * self.i
            return Complex(r, i)

        if isinstance(number, MagicStr):
            raise ValueError('Cannot multiplie Complex w/MagicStr')

        return Complex(self.r * number, self.i * number)

    def __rmul__(self, number):
        return self.__mul__(number)

    def __truediv__(self, number):
        if isinstance(number, Complex):
            r = (
                (self.r * number.r + self.i * number.i)
                / (ft_power(number.r, 2) + ft_power(number.i, 2))
            )
            i = (
                (self.i * number.r - number.i * self.r)
                / (ft_power(number.r, 2) + ft_power(number.i, 2))
            )
            return Complex(r, i)

        if isinstance(number, MagicStr):
            raise ValueError('Cannot divide Complex w/MagicStr')

        return Complex(self.r / number, self.i / number)

    def __rtruediv__(self, number):
        if isinstance(number, Complex):
            number.__truediv__(self)

        return Complex(number, 0) / self

    def __floordiv__(self, _):
        raise TypeError('Cannot do a floor div with Complex object')

    def __rfloordiv__(self, _):
        raise TypeError('Cannot do a floor div with Complex object')

    def __mod__(self, _):
        raise TypeError('Cannot do a modulo with Complex object')

    def __rmod__(self, _):
        raise TypeError('Cannot do a modulo with Complex object')

    def __neg__(self):
        #XXX: Hack to work w/unary minus and my own core parser
        return Complex(self.r, -self.i)

class Matrix:
    def __init__(self, value):
        """Supposed that value is a 2d list of numbers."""
        self.dimension = (0, 0)
        self.matrix = value

    @property
    def x(self):
        return self.dimension[0]

    @property
    def y(self):
        return self.dimension[1]

    def column(self, index):
        return [elem[index] for elem in self.matrix]

    def line(self, index):
        return self.matrix[index]

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        y = len(value)
        x = len(value[0])

        for elem in value:
            mx = len(elem)

            if mx != x:
                raise ValueError(
                    'Incorrect Matrix: all lines should have the same lenght.'
                )

        self.dimension = (x, y)
        self._matrix = value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '\n'.join(map(str, self.matrix)).replace('"', '')

    def to_magic_str(self):
        return '[%s]' % str(self).replace('\n', '; ')

    def __getitem__(self, key):
        return self.matrix[key]

    def __setitem__(self, key, value):
        self.matrix[key] = value

    def matrix_mul(self, elem):
        if self.x != elem.y:
            raise ValueError(
'''
Width of first Matrix should be equal to the height of the second one:
{x} != {y}
'''.format(x=self.x, y=elem.y)
)
        final_matrix = list()

        for index, line in enumerate(self.matrix):
            new_line = list()

            for col_index in range(elem.x):
                new_elem = sum(
                    [a * b for a, b in zip(line, elem.column(col_index))]
                )

                new_line.append(new_elem)

            final_matrix.append(new_line)

        return Matrix(final_matrix)

    def _do_matrix_operation(self, elem, operation):
        final_matrix = []

        if isinstance(elem, Matrix):
            if elem.dimension != self.dimension:
                raise ValueError('Both Matrix should have the same dimension.')

            for line_m1, line_m2 in zip(self.matrix, elem.matrix):
                final_matrix.append(list())

                for a, b in zip(line_m1, line_m2):
                    result = getattr(operator, operation)(a, b)
                    final_matrix[-1].append(result)
        else:
            for line in self.matrix:
                final_matrix.append(list())

                for a in line:
                    result = getattr(operator, operation)(a, elem)
                    final_matrix[-1].append(result)

        return Matrix(final_matrix)

    def __add__(self, elem):
        return self._do_matrix_operation(elem, 'add')

    def __radd__(self, elem):
        return self.__add__(elem)

    def __sub__(self, elem):
        return self._do_matrix_operation(elem, 'sub')

    def __rsub__(self, elem):
        if not isinstance(elem, Matrix):
            #XXX: Not the better way to this just a lazy way.
            x = self.x
            y = self.y
            elem = Matrix([[elem for _ in range(x)] for __ in range(y)])

        return elem.__sub__(self)


    def __mul__(self, elem):

        if not isinstance(elem, Matrix):
            return self._do_matrix_operation(elem, 'mul')

        raise SyntaxError('You should use `**` for Matrix multiplications.')

    def __rmul__(self, elem):
        return self.__mul__(elem)

    def __truediv__(self, elem):
        return self._do_matrix_operation(elem, 'truediv')

    def __rtruediv__(self, elem):
        if not isinstance(elem, Matrix):
            #XXX: Not the better way to this just a lazy way.
            x = self.x
            y = self.y
            elem = Matrix([[elem for _ in range(x)] for __ in range(y)])

        return elem.__truediv__(self)
