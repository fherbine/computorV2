import copy
import itertools
import re
from collections import namedtuple

from core.lexer import Token

BNF_GRAMAR_RULES = []
RULES = {}
DEBUG = False
Production = namedtuple('Production', ['returned_type', 'method'])

class ParserError(Exception):
    pass


class ParsedItem:
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def __str__(self):
        return '{cls}(identifier={identifier}, value={value})'.format(
            cls=type(self).__name__,
            identifier=self.identifier,
            value=repr(self.value),
        )

    def __repr__(self):
        return str(self)


class ParsedItemsList:
    """This class represents a list of objects types ParsedItem."""
    items = []

    def __init__(self, items):
        self.items = items
        self.items_identifier = [item.identifier for item in items]

    def __getitem__(self, index):
        fetched_parsed_item = self.items[index]
        return fetched_parsed_item.value

    def __getattr__(self, attr):
        base_attr = re.sub(r'\d+$', '', attr)
        index = re.search(r'\d+$', attr)
        index = int(index.group()) if index else 0

        if base_attr not in self.items_identifier:
            raise AttributeError('%s is not in BNF definition.' % base_attr)

        compatible_items = [
            item for item in self.items if item.identifier == base_attr
        ]

        fetched_parsed_item = compatible_items[index]

        return fetched_parsed_item.value

    def __str__(self):
        return '{cls}({content})'.format(
            cls=type(self).__name__,
            content=[repr(item) for item in self.items],
        )

    def __len__(self):
        return len(self.items)


class LiteralBnfRule:
    def __init__(self, string):
        self.string = string

    def __len__(self):
        return len(self.string.split(' '))

    def __str__(self):
        return self.string

    def __repr__(self):
        return '{cls}({rpr})'.format(
            cls=type(self).__name__,
            rpr=repr(self.string)
        )

    def __iter__(self):
        self.n = -1
        return self

    def __next__(self):
        tab = self.string.split(' ')
        self.n += 1

        if self.n >= len(tab):
            raise StopIteration()

        return tab[self.n]

    def __getitem__(self, index):
        return self.string.split(' ')[index]

    def __contains__(self, rule):
        return '%s' % rule in self.string.split(' ')

    def __eq__(self, other):
        if not isinstance(other, LiteralBnfRule):
            return False

        return self.string == other.string

    def index(self, rule):
        for index, _rule in enumerate(self):
            if rule == _rule:
                return index

    def search(self, statement):
        if isinstance(statement, str):
            statement = LiteralBnfRule(statement)

        statement_len = len(statement)

        for index in range(len(self)):
            potential_statement = LiteralBnfRule(' '.join(self[index:index+statement_len]))

            if potential_statement == statement:
                return index

            if index >= len(self) - statement_len:
                return

    def without_prec(self):
        return LiteralBnfRule(re.sub(' %prec.*$', '', self.string))


def add_production_to_rules(production, *bnf_rules):
    global RULES

    for rule in bnf_rules:
        RULES[rule] = production


def _(*bnf_rules):
    global BNF_GRAMAR_RULES

    if bnf_rules not in BNF_GRAMAR_RULES:
        BNF_GRAMAR_RULES += [LiteralBnfRule(rule) for rule in bnf_rules]

    def decorator(method):
        returned_type = method.__name__
        production = Production(returned_type, method)
        add_production_to_rules(production, *bnf_rules)

        def modified_func(self, parsed):
            # function call
            return method(self, parsed)

        return modified_func
    return decorator


class CoreParser:
    tokens = []
    precedence = []

    def __init__(self):
        self.reset()
        self._sort_rules()

    def reset(self):
        self._statements_stack = []
        self._items_stack = []

    def _sort_rules(self):
        tmp = list()
        global BNF_GRAMAR_RULES

        for prec in reversed(self.precedence):
            side, *operators = prec

            for operator in operators:
                for bnf_rule in BNF_GRAMAR_RULES:
                    if bnf_rule in tmp:
                        continue

                    if operator in str(bnf_rule):
                        tmp += [bnf_rule]
                        continue

        self._not_prec_rules = sorted([rule for rule in BNF_GRAMAR_RULES if rule not in tmp], key=len, reverse=True)
        tmp += self._not_prec_rules

        BNF_GRAMAR_RULES = tmp


    def _is_identifier_in_bnf_rules(self, item):
        return item.identifier in BNF_GRAMAR_RULES

    def _to_parsed_item(self, elem):
        if not isinstance(elem, Token):
            # stil a parsed item
            return elem

        return ParsedItem(elem.token_type, elem.value)

    def _call_production(self, statement_key, parsed_items):
        production = RULES[statement_key]
        new_identifier = production.returned_type
        new_value = production.method(self, parsed_items)

        if DEBUG:
            print('call', statement_key, parsed_items, 'new_val: ', new_value, 'new_id:', new_identifier)

        return ParsedItem(new_identifier, new_value)

    def _resolve_single_item(self, item):
        available_statements = [statement for statement in BNF_GRAMAR_RULES if item.identifier in statement]

        if len(available_statements) == 1 and len(available_statements[0]) == 1:
            statement_key = str(available_statements[0])
            return self._call_production(statement_key, ParsedItemsList([item]))

        return item

    def _resolve_first_selected_statement(self, statement, index, with_prec=''):
        # suppose that statement while be litteral bnf
        items = self._items_stack[index:len(statement) + index]
        statement_key = str(statement)
        new_item = self._call_production(statement_key + with_prec, ParsedItemsList(items))
        del self._items_stack[index:len(statement) + index]
        self._items_stack.insert(index, new_item)
        self._statements_stack = [item.identifier for item in self._items_stack]

    def _resolve_multiple_items(self):
        literal = LiteralBnfRule(' '.join(self._statements_stack))
        potential_prec = None

        for prec in reversed(self.precedence):
            # Handling left prec
            side, *operators = prec

            if side in ('left', 'maximum'):
                continue

            for operator in operators:
                available_statements = [statement for statement in BNF_GRAMAR_RULES if operator in statement]
                # removing ' %prec OPER...'
                clean_available_statements = [statement.without_prec() for statement in available_statements]

                for index, statement in enumerate(clean_available_statements):
                    statement_index = literal.search(statement)

                    if statement_index is None:
                        continue

                    with_prec=re.sub(str(statement), '', str(available_statements[index]))
                    potential_prec = (statement, statement_index, with_prec)

                    break

        index = None
        match_rule = None
        operator_levels = []
        previous_max = -1

        for prec_level, prec in enumerate(reversed(self.precedence)):
            side, *operators = prec
            with_prec = ''

            if side == 'maximum':
                operator = operators[0]
                max_operator = operator
                previous_max = literal.search(operator)
                previous_max = -1 if previous_max is None else previous_max

            if side == 'right':
                continue

            available_statements = []

            for operator in operators:
                available_statements += [(prec_level, statement) for statement in BNF_GRAMAR_RULES if operator in statement and operator in literal]

            operator_index = literal.index(operator)

            for statement_level, statement in available_statements:
                statement_index = literal.search(statement)

                if statement_index is None:
                    continue

                literal_copy = LiteralBnfRule(literal.string)

                offset = 0
                while (statement_index is None or statement_index < previous_max) and max_operator not in statement:
                    literal_copy = literal_copy.string

                    if not literal_copy:
                        break

                    offset += 1
                    literal_copy = LiteralBnfRule(' '.join(literal_copy.split(' ')[1:]))

                    statement_index = literal_copy.search(statement)

                    if statement_index is None:
                        continue

                    statement_index += offset

                if statement_index is None:
                    continue


                if index is None or statement_index < index:
                    index = statement_index
                    match_rule = (statement, statement_index, with_prec)

            if match_rule:
                self._resolve_first_selected_statement(*match_rule)
                return

        index = None
        previous_len = None
        possible_solution = -1
        gliteral = literal

        for _statement in self._not_prec_rules:
            #FIXME: Need to search for the lower index
            statement_index = literal.search(_statement)

            if statement_index is None:
                continue

            statement_return = RULES[str(_statement)].returned_type
            statement_possible_solution = len([_ for _ in RULES if statement_return in LiteralBnfRule(_)])

            if index is None or (statement_index < index or statement_possible_solution > possible_solution) and statement_possible_solution > 1:
                index = statement_index
                statement = _statement
                possible_solution = statement_possible_solution
                previous_len = len(_statement)

        left_prec = potential_prec
        literal = gliteral

        if left_prec:
            left_idx = left_prec[1]
            left_stmt = left_prec[0]
            pr = left_prec[-1]
            left_operators = list(itertools.chain.from_iterable([op[1:] for op in reversed(self.precedence) if op[0] == 'left']))
            previous_rule_kw = literal[left_idx-1]
            statement_return = RULES[str(left_stmt) + pr].returned_type
            statement_possible_solution = len([_ for _ in RULES if statement_return in LiteralBnfRule(_)])

            if index is None:
                return

            if (
                previous_rule_kw in left_operators
                or left_idx < index
                or (
                    statement_possible_solution > possible_solution
                    and possible_solution <= 1
                )
            ):
                statement, index, with_prec = left_prec

        if index is None:
            return

        self._resolve_first_selected_statement(statement, index, with_prec)
        return

    def _resolve_stack(self):
        if len(self._items_stack) == 1 and self._items_stack[0].identifier not in list(RULES.keys()):
            for rule in RULES:
                if self._items_stack[0].identifier in LiteralBnfRule(rule):
                    self.error(None)
            return bool(self._items_stack[0].identifier not in self.tokens)

        cmp_stack = copy.copy(self._items_stack)

        if DEBUG:
            print('[0] statements stack:', self._statements_stack)

        self._items_stack = [self._resolve_single_item(item) for item in self._items_stack]

        self._statements_stack = [item.identifier for item in self._items_stack]
        if DEBUG:
            print('[1] statements stack:', self._statements_stack)
        self._resolve_multiple_items()

        if cmp_stack == self._items_stack:
            #XXX: Hack to raise error + nothing passed not like in sly
            if DEBUG:
                print('statements stack:', self._statements_stack, 'itm stck', self._items_stack)
            self.error(None)

        return self._resolve_stack()

    def parse(self, tokens_it):
        self.reset()

        for token in tokens_it:
            parsed_item = self._to_parsed_item(token)

            if token.token_type not in self.tokens:
                raise ParserError('Cannot find token %s' % token.token_type)

            self._items_stack.append(parsed_item)
            self._statements_stack.append(parsed_item.identifier)

        if DEBUG:
            print('statements stack:', self._statements_stack, 'itm stck', self._items_stack)

        resolved = self._resolve_stack()

        if not resolved:
            self.error(None)

        return self._items_stack[0].value

    def error(self, _):
        raise ParserError('Parser ERROR')



if __name__ == '__main__':
    from lexer import CoreLexer

    class _TstLexer(CoreLexer):
        tokens = [ 'NUMBER', 'ADD', 'TIMES', 'MINUS', 'DIVIDE',
                   'LPAREN', 'RPAREN', 'ID' ]
        ignore = ' \t'

        NUMBER = r'\d+'
        ADD = r'\+'
        MINUS = r'-'
        DIVIDE = r'/'
        TIMES = r'\*'
        LPAREN = r'\('
        RPAREN = r'\)'
        ID = r'[a-zA-Z]+'


        def token_NUMBER(self, token):
            token.value = int(token.value)
            return token


    class _TstParser(CoreParser):
        tokens = _TstLexer.tokens
        precedence = (
            ('left', 'MINUS', 'ADD'),
            ('left', 'TIMES', 'DIVIDE'),
            ('right', 'UMINUS'),
        )

        @_('expr')
        def statement(self, parsed):
            return parsed.expr

        @_('expr TIMES expr')
        def expr(self, parsed):
            return parsed[0] * parsed[2]

        @_('expr DIVIDE expr')
        def expr(self, parsed):
            return parsed.expr0 / parsed.expr1

        @_('expr ADD expr')
        def expr(self, parsed):
            return parsed[0] + parsed[2]

        @_('expr MINUS expr')
        def expr(self, parsed):
            return parsed.expr0 - parsed.expr1

        @_('MINUS expr %prec UMINUS')
        def expr(self, parsed):
            return -parsed.expr

        @_('ID LPAREN expr RPAREN')
        def statement(self, parsed):
            return 'func'

        @_('LPAREN expr RPAREN')
        def expr(self, parsed):
            return parsed.expr

        @_('ID')
        def expr(self, parsed):
            return 0

        @_('NUMBER')
        def expr(self, parsed):
            return parsed.NUMBER


    lexer = _TstLexer()
    parser = _TstParser()

    while True:
        line = input('> ')

        if line:
            toks = lexer.tokenize(line)
            print(parser.parse(toks))
