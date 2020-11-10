import os
import sys

PLATFORM = 'win' if os.name == 'nt' else 'unix'

def fancy_hello():
    os.system('clear')
    v2 = '''
      ::::::::   ::::::::    :::   :::   :::::::::  :::    ::: ::::::::::: ::::::::  :::::::::  :::     :::  ::::::::
    :+:    :+: :+:    :+:  :+:+: :+:+:  :+:    :+: :+:    :+:     :+:    :+:    :+: :+:    :+: :+:     :+: :+:    :+:
   +:+        +:+    +:+ +:+ +:+:+ +:+ +:+    +:+ +:+    +:+     +:+    +:+    +:+ +:+    +:+ +:+     +:+       +:+
  +#+        +#+    +:+ +#+  +:+  +#+ +#++:++#+  +#+    +:+     +#+    +#+    +:+ +#++:++#:  +#+     +:+     +#+
 +#+        +#+    +#+ +#+       +#+ +#+        +#+    +#+     +#+    +#+    +#+ +#+    +#+  +#+   +#+    +#+
#+#    #+# #+#    #+# #+#       #+# #+#        #+#    #+#     #+#    #+#    #+# #+#    #+#   #+#+#+#    #+#
########   ########  ###       ### ###         ########      ###     ########  ###    ###     ###     ##########
'''
    if PLATFORM == 'unix':
        os.system('echo "%s" | lolcat' % v2)
        os.system('echo "by fherbine" | lolcat')
    else:
        print(v2, '\nby fherbine')
    print('\n\n')

def draw(functions):
    while True:
        function = input(
            'Fonction identifier %s: ' % [k.lower() for k in functions.keys()]
        )

        if function.upper() in functions:
            break
        print('Unknown function %s' % function)

    function = functions[function.upper()]

    formula = '[({arg}, {body}) for {arg} in range%s]'.format(
        arg=function.args[0],
        body=str(function.body).replace('^', '**'),
    )

    default = input('use default param [Y/n]:').upper() != 'N'
    kwargs = {}

    while not default:
        try:
            kwargs = {
                'xmin': int(input('xmin: ')),
                'xmax': int(input('xmax: ')),
                'ymin': int(input('ymin: ')),
                'ymax': int(input('ymax: ')),
            }
            break
        except:
            print('min/max value must be integer.')
            continue

    return 'draw', formula, kwargs

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

    def __neg__(self):
        #XXX: Hack to work w/unary minus and my own core parser
        unknown = self.unknown
        return MagicStr(f'-{self.string}', unknown)

    def _do_magic_operation(self, elem, op, name, reverse=False):
        unknown = self.unknown

        if isinstance(elem, MagicStr):
            unknown = self.unknown + elem.unknown

        if type(elem).__name__ == 'Matrix':
            return getattr(elem, name)(self)

        if not reverse:
            return MagicStr(f'{self.string} {op} {elem}', unknown)

        return MagicStr(f'{elem} {op} {self.string}', unknown)

    # normal operations (self operator object)
    def __add__(self, obj):
        return self._do_magic_operation(obj, '+', '__add__')

    def __sub__(self, obj):
        return self._do_magic_operation(obj, '-', '__sub__')

    def __mul__(self, obj):
        return self._do_magic_operation(obj, '*', '__mul__')

    def __truediv__(self, obj):
        return self._do_magic_operation(obj, '/', '__truediv__')

    def __floordiv__(self, obj):
        return self._do_magic_operation(obj, '//', '__floordiv__')

    def __mod__(self, obj):
        return self._do_magic_operation(obj, '%', '__mod__')

    #Reverse operations (object self, operator)
    def __radd__(self, obj):
        return self._do_magic_operation(obj, '+', '__radd__', reverse=True)

    def __rsub__(self, obj):
        return self._do_magic_operation(obj, '-', '__rsub__', reverse=True)

    def __rmul__(self, obj):
        return self._do_magic_operation(obj, '*', '__rmul__', reverse=True)

    def __rtruediv__(self, obj):
        return self._do_magic_operation(obj, '/', '__rtruediv__', reverse=True)

    def __rfloordiv__(self, obj):
        return self._do_magic_operation(obj, '//', '__rfloordiv__', reverse=True)

    def __rmod__(self, obj):
        return self._do_magic_operation(obj, '%', '__rmod__', reverse=True)
