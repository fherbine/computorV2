import os
import sys

def fancy_hello():
    os.system('clear')
    v2 = '''"
        CCCCCCCCCCCCC                                                                                      tttt                                           VVVVVVVV           VVVVVVVV 222222222222222
     CCC::::::::::::C                                                                                   ttt:::t                                           V::::::V           V::::::V2:::::::::::::::22
   CC:::::::::::::::C                                                                                   t:::::t                                           V::::::V           V::::::V2::::::222222:::::2
  C:::::CCCCCCCC::::C                                                                                   t:::::t                                           V::::::V           V::::::V2222222     2:::::2
 C:::::C       CCCCCC   ooooooooooo      mmmmmmm    mmmmmmm   ppppp   ppppppppp   uuuuuu    uuuuuuttttttt:::::ttttttt       ooooooooooo   rrrrr   rrrrrrrrrV:::::V           V:::::V             2:::::2
C:::::C               oo:::::::::::oo  mm:::::::m  m:::::::mm p::::ppp:::::::::p  u::::u    u::::ut:::::::::::::::::t     oo:::::::::::oo r::::rrr:::::::::rV:::::V         V:::::V              2:::::2
C:::::C              o:::::::::::::::om::::::::::mm::::::::::mp:::::::::::::::::p u::::u    u::::ut:::::::::::::::::t    o:::::::::::::::or:::::::::::::::::rV:::::V       V:::::V            2222::::2
C:::::C              o:::::ooooo:::::om::::::::::::::::::::::mpp::::::ppppp::::::pu::::u    u::::utttttt:::::::tttttt    o:::::ooooo:::::orr::::::rrrrr::::::rV:::::V     V:::::V        22222::::::22
C:::::C              o::::o     o::::om:::::mmm::::::mmm:::::m p:::::p     p:::::pu::::u    u::::u      t:::::t          o::::o     o::::o r:::::r     r:::::r V:::::V   V:::::V       22::::::::222
C:::::C              o::::o     o::::om::::m   m::::m   m::::m p:::::p     p:::::pu::::u    u::::u      t:::::t          o::::o     o::::o r:::::r     rrrrrrr  V:::::V V:::::V       2:::::22222
C:::::C              o::::o     o::::om::::m   m::::m   m::::m p:::::p     p:::::pu::::u    u::::u      t:::::t          o::::o     o::::o r:::::r               V:::::V:::::V       2:::::2
 C:::::C       CCCCCCo::::o     o::::om::::m   m::::m   m::::m p:::::p    p::::::pu:::::uuuu:::::u      t:::::t    tttttto::::o     o::::o r:::::r                V:::::::::V        2:::::2
  C:::::CCCCCCCC::::Co:::::ooooo:::::om::::m   m::::m   m::::m p:::::ppppp:::::::pu:::::::::::::::uu    t::::::tttt:::::to:::::ooooo:::::o r:::::r                 V:::::::V         2:::::2       222222
   CC:::::::::::::::Co:::::::::::::::om::::m   m::::m   m::::m p::::::::::::::::p  u:::::::::::::::u    tt::::::::::::::to:::::::::::::::o r:::::r                  V:::::V          2::::::2222222:::::2
     CCC::::::::::::C oo:::::::::::oo m::::m   m::::m   m::::m p::::::::::::::pp    uu::::::::uu:::u      tt:::::::::::tt oo:::::::::::oo  r:::::r                   V:::V           2::::::::::::::::::2
        CCCCCCCCCCCCC   ooooooooooo   mmmmmm   mmmmmm   mmmmmm p::::::pppppppp        uuuuuuuu  uuuu        ttttttttttt     ooooooooooo    rrrrrrr                    VVV            22222222222222222222
                                                               p:::::p
                                                               p:::::p
                                                              p:::::::p
                                                              p:::::::p
                                                              p:::::::p
                                                              ppppppppp
"'''
    os.system('echo %s | lolcat' % v2)
    os.system('echo "by fherbine" | lolcat')
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
