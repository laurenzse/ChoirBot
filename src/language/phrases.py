from src.language.context_free_grammar import ContextFreeGrammar, cleanup

GRAMMAR_NAME = 'src/language/language_grammar.cfg'

grammar = ContextFreeGrammar()
grammar.add_productions_from_file(GRAMMAR_NAME)

name_symbol = cleanup(grammar.gen_random_convergent('name'))


def formulate(sentence_name):
    return cleanup(grammar.gen_random_convergent(sentence_name))


class PersonalPhrases:

    def __init__(self, member):
        self.member = member

    def formulate(self, sentence_name):
        impersonal = formulate(sentence_name)
        return impersonal.replace(name_symbol, self.member.first_name)