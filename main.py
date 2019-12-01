from controllers.lexer import BcLexer
from controllers.parser import BcParser
from controllers.polynomial_lexparse import PolyLexer
from controllers.utils import exit_bc

if __name__ == '__main__':
    lexer = BcLexer()
    parser = BcParser()
    lex = PolyLexer()

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
                parser.parsed_str = data
                result = parser.parse(lexer.tokenize(data))

                if result is None:
                    print('Nothing to be done.')
                else:
                    print(result)
            except Exception as e:
                print(e)
