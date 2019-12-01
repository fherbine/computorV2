import os
import sys

def fancy_hello():
    os.system('clear')
    os.system('echo ComputorV2 | figlet | lolcat')
    os.system('echo "by fherbine" | lolcat')
    print('\n\n')

def exit_bc():
    print('quit')
    sys.exit(0)

class MagicStr:
    def __init__(self, value, unknown=''):
        self.string = value
        self.unknown = unknown

    def __repr__(self):
        return '"%s"' % self.string

    def __str__(self):
        return self.string

    def _do_magic_operation(self, elem, op, reverse=False):
        unknown = self.unknown

        if isinstance(elem, MagicStr):
            unknown = self.unknown + elem.unknown

        if not reverse:
            return MagicStr(f'{self.string} {op} {elem}', unknown)

        return MagicStr(f'{elem} {op} {self.string}', unknown)

    # normal operations (self operator object)
    def __add__(self, obj):
        return self._do_magic_operation(obj, '+')

    def __sub__(self, obj):
        return self._do_magic_operation(obj, '-')

    def __mul__(self, obj):
        return self._do_magic_operation(obj, '*')

    def __truediv__(self, obj):
        return self._do_magic_operation(obj, '/')

    def __floordiv__(self, obj):
        return self._do_magic_operation(obj, '//')

    def __mod__(self, obj):
        return self._do_magic_operation(obj, '%')

    #Reverse operations (object self, operator)
    def __radd__(self, obj):
        return self._do_magic_operation(obj, '+', reverse=True)

    def __rsub__(self, obj):
        return self._do_magic_operation(obj, '-', reverse=True)

    def __rmul__(self, obj):
        return self._do_magic_operation(obj, '*', reverse=True)

    def __rtruediv__(self, obj):
        return self._do_magic_operation(obj, '/', reverse=True)

    def __rfloordiv__(self, obj):
        return self._do_magic_operation(obj, '//', reverse=True)

    def __rmod__(self, obj):
        return self._do_magic_operation(obj, '%', reverse=True)
