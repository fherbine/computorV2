import queue
import re
import threading

from kivy.utils import platform

from controllers.lexer import BcLexer
from controllers.parser import BcParser
from controllers.polynomial_lexparse import PolyLexer
from controllers.utils import exit_bc, fancy_hello
from controllers.graph import FunGraphApp, reset_window

class GraphThread(threading.Thread):
    def __init__(self, formula_queue):
        self.formula_queue = formula_queue
        self.app = None

        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                formula = self.formula_queue.get_nowait()
            except queue.Empty:
                continue

            if platform == 'macosx':
                print('Sorry you cannot use this command on %s' % platform)
                continue

            reset_window()
            app = FunGraphApp()
            app.create_curve(*formula)
            app.run()

if __name__ == '__main__':
    lexer = BcLexer()
    parser = BcParser()
    lex = PolyLexer()
    formula_queue = queue.Queue()

    #Thread to draw functions graphs.
    graph_thread = GraphThread(formula_queue).start()

    fancy_hello()

    while True:
        try:
            data = input('> ')
        except KeyboardInterrupt:
            # Raised if SIGINT (Ctrl+C) is raised
            print('')
            continue

        except EOFError:
            # Ctrl + D
            exit_bc()


        if data:
            try:
                #XXX: Hack for implicits times
                data = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', data)
                parser.parsed_str = data
                result = parser.parse(lexer.tokenize(data))

                if isinstance(result, list) or isinstance(result, tuple):
                    func, args, kwargs = result

                    if func == 'draw':
                        formula_queue.put((args, kwargs))
                    continue

                if result is None:
                    print('Nothing to be done.')
                else:
                    print(result)
            except Exception as e:
                print(e)

    graph_thread.join(.2)
