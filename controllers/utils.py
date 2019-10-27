import sys

def exit_bc():
    print('quit')
    sys.exit(0)

class MagicStr:
    def __init__(self, value):
        self.string = value

    def __repr__(self):
        return '"%s"' % self.string

    def __str__(self):
        return self.string

    # normal operations (self operator object)
    def __add__(self, obj):
        return MagicStr(f'{self.string} + {obj}')

    def __sub__(self, obj):
        return MagicStr(f'{self.string} - {obj}')

    def __mul__(self, obj):
        return MagicStr(f'{self.string} * {obj}')

    def __truediv__(self, obj):
        return MagicStr(f'{self.string} / {obj}')

    def __floordiv__(self, obj):
        return MagicStr(f'{self.string} // {obj}')

    def __mod__(self, obj):
        return MagicStr(f'{self.string} % {obj}')

    #Reverse operations (object self, operator)
    def __radd__(self, obj):
        return MagicStr(f'{obj} + {self.string}')

    def __rsub__(self, obj):
        return MagicStr(f'{obj} - {self.string}')

    def __rmul__(self, obj):
        return MagicStr(f'{obj} * {self.string}')

    def __rtruediv__(self, obj):
        return MagicStr(f'{obj} / {self.string}')

    def __rfloordiv__(self, obj):
        return MagicStr(f'{obj} // {self.string}')

    def __rmod__(self, obj):
        return MagicStr(f'{obj} % {self.string}')
