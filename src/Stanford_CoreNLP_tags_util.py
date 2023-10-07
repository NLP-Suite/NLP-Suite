# V2 REVISED INTRODUCTION https://universaldependencies.org/u/feat/index.html
# V2 REVISED POS TAGS https://universaldependencies.org/u/pos/index.html
# V2 REVISED DEPREL TAGS https://universaldependencies.org/u/dep/all.html

# D: Added AFX, FW, HYPH, NFP, -LRB-, -RRB-. See https://spacy.io/api/annotation
dict_POSTAG = {'AFX': 'Affix', \
               'CC': 'Coordinating conjunction', \
               'CD': 'Cardinal number', \
               'DT': 'Determinant', \
               'EX': 'Existential there', \
               'FW': 'Foreign word', \
               'HYPH': 'Punctuation Mark, hyphen', \
               'IN': 'Preposition or subordinating conjunction', \
               'JJ': 'Adjective', \
               'JJR': 'Adjective, comparative', \
               'JJS': 'Adjective, superlative', \
               'LS': 'List marker', \
               'MD': 'Modal verb', \
               'NFP': 'Superfluous punctuation', \
               'NN': 'Noun, singular or mass', \
               'NNS': 'Noun, plural', \
               'NNP': 'Proper noun, singular', \
               'NNPS': 'Proper noun, plural', \
               'PDT': 'Predeterminer', \
               'POS': 'Possessive ending', \
               'PRP': 'Personal pronoun', \
               'PRP$': 'Possessive pronoun', \
               'RB': 'Adverb', \
               'RBR': 'Adverb, comparative', \
               'RBS': 'Adverb, superlative', \
               'RP': 'Particle', \
               'SYM': 'Symbol', \
               'TO': 'To', \
               'UH': 'Interjection', \
               'VB': 'Verb, base form', \
               'VBD': 'Verb, past tense', \
               'VBG': 'Verb, gerund or present participle', \
               'VBN': 'Verb, past participle', \
               'VBP': 'Verb, non-3rd person singular present', \
               'VBZ': 'Verb, 3rd person singular present', \
               'WDT': 'Wh-determiner (what, which, whose)', \
               'WP': 'Wh-pronoun (how, what, which, where, when, who, whom, whose, whether', \
               'WP$': 'Possessive wh-pronoun', \
               'WRB': 'Wh-adverb (when, where, how, and why)', \
               '(': '(', \
               ')': ')', \
               '.': '.', \
               ',': '.', \
               ':': ':', \
               '\'': '\'', \
               # D: There is also a `` tag, which is different from ".
               '``': '``', \
               '\"': '\"', \
               '#': '#', \
               '-LRB-': 'Left round bracket', \
               '-RRB-': 'Right round bracket'
               }

# list of possible deprel values
# V2 REVISED TAGS https://universaldependencies.org/u/dep/all.html

dict_DEPREL = {
    # D: acl is often followed by:
    # above, along, as, at, because_of, by, for, in, of, on
    # over, though, to, with,
    # as in acl:above
    'acl': 'clausal modifier of noun (adjectival clause)', \
    'acl:relcl': 'relative clause modifier', \
    # D: I am not able to find acomp in documentation. Is it renamed?
    'acomp': 'adjectival complement', \
    # D: advcl also combines with other words a lot. Such as advcl:about
    # after against along although as as_if as_to at...
    'advcl': 'adverbial clause modifier', \
    'advmod': 'adverbial modifier', \
    'agent': 'agent', \
    'amod': 'adjectival modifier', \
    'appos': 'appositional modifier', \
    'arg': 'argument', \
    'aux': 'auxiliary', \
    'aux:pass': 'passive auxiliary', \
    'case': 'case marking', \
    'cc': 'coordinating conjunction', \
    'ccomp': 'clausal complement with internal subject', \
    'cc:preconj': 'preconjunct', \
    'compound': 'compound', \
    'compound:prt': 'phrasal verb particle', \
    'conj': 'conjunct', \
    'cop': 'copula conjunction', \
    'csubj': 'clausal subject', \
    'csubj:pass': 'clausal passive subject', \
    'dep': 'unspecified dependency', \
    'det': 'determiner', \
    'det:predet': 'predeterminer', \
    'discourse': 'discourse element', \
    'dislocated': 'dislocated element', \
    'obj': 'object', \
    'expl': 'expletive', \
    # 'foreign': 'foreign words', \ used in V1 but no longer used in V2 substituted by flat:foreign
    'fixed': 'fixed multiword expression (MWE)', \
    # flat is the opposite of fixed
    'flat': 'flat: flat multiword expression (MWE)', \
    'flat:foreign': 'foreign words', \
    'goeswith': 'goes with', \
    'iobj': 'indirect object', \
    'list': 'list', \
    'mark': 'marker', \
    'mod': 'modifier', \
    'mwe': 'multi-word expression', \
    'name': 'name', \
    'neg': 'negation modifier', \
    'nn': 'noun compound modifier', \
    # D: Same for nmod
    'nmod': 'nominal modifier', \
    'nmod:agent': 'agents of passive sentences', \
    'nmod:npmod': 'noun phrase as adverbial modifier', \
    'nmod:poss': 'possessive nominal modifier', \
    'nmod:tmod': 'temporal modifier', \
    'nummod': 'numeric modifier', \
    'npadvmod': 'noun phrase adverbial modifier', \
    'nsubj': 'nominal subject', \
    'nsubj:pass': 'passive nominal subject', \
    # D: Added the following two lines
    'nsubj:xsubj': 'nominal subject of controlled verbs',
    'nsubj:pass:xsubj': 'passive nominal subject of controlled verbs',
    'num': 'numeric modifier', \
    'number': 'element of compound number', \
    # obl is often followed by at, in, to, as in obl:in
    'obl': 'oblique nominal', \
    'parataxis': 'parataxis', \
    'pcomp': 'prepositional complement', \
    'pobj': 'object of a preposition', \
    'poss': 'possession modifier', \
    'possessive': 'possessive modifier', \
    'preconj': 'preconjunct', \
    'predet': 'predeterminer', \
    'prep': 'prepositional modifier', \
    'prepc': 'prepositional clausal modifier', \
    'prt': 'phrasal verb particle', \
    'punct': 'punctuation', \
    'quantmod': 'quantifier phrase modifier', \
    'rcmod': 'relative clause modifier', \
    'ref': 'referent', \
    'remnant': 'remnant in ellipsis', \
    'reparandum': 'overridden disfluency', \
    'root': 'root of the tree', \
    'ROOT': 'root of the tree', \
    'sdep': 'semantic dependent', \
    'subj': 'subject', \
    'tmod': 'temporal modifier', \
    'vmod': 'reduced non-finite verbal modifier', \
    'vocative': 'vocative', \
    'xcomp': 'clausal complement with external subject', \
    'xsubj': 'controlling subject', \
    '#': '#'
}

acl_subs = ['above', 'along', 'as', 'at', 'because_of', 'by', 'for',
               'in', 'of', 'on', 'over', 'though', 'to', 'with']
advcl_subs = ['about', 'after', 'against', 'along', 'although', 'as', 'as_if', 'as_to',
              'at', 'because', 'before', 'by', 'for', 'from', 'if', 'in', 'in_order', 'instead_of',
              'into', 'lest', 'like', 'of', 'off', 'on', 'once', 'since', 'so', 'so_that',
              'that', 'than', 'though', 'through', 'till', 'to', 'toward', 'unless', 'until', 'upon',
              'whence', 'whereon', 'whether', 'while', 'whither', 'with', 'without']
nmod_subs = ['\'', '\'s', 'about', 'above', 'across', 'after', 'against', 'ago', 'along',
             'among', 'around', 'as', 'at', 'before', 'behind', 'beneath', 'beside',
             'between', 'beyond', 'but', 'by', 'for', 'from', 'full', 'in', 'inside',
             'instead_of', 'into', 'like', 'near', 'of', 'on', 'once', 'outside',
             'over', 'past', 'poss', 'regarding', 'such_as', 'than', 'that', 'through', 'to',
             'under', 'up', 'with', 'without']
obl_subs = ['\'s', 'aboard', 'above', 'about', 'according_to', 'across', 'after', 'against', 'agent',
            'ago', 'along', 'amid', 'among', 'around', 'as', 'as_to', 'at', 'because', 'because_of',
            'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but',
            'by', 'down', 'during', 'following', 'for', 'from', 'in', 'into', 'like', 'near', 'npmod',
            'of', 'off', 'on', 'once', 'out', 'outside', 'over', 'past', 'regarding', 'save', 'since',
            'than', 'through', 'throughout', 'till', 'tmod', 'to', 'toward', 'towards', 'under',
            'until', 'up', 'upon', 'whence', 'while', 'with', 'within', 'without']

deprel_mapping = {'acl': acl_subs,
                  'advcl': advcl_subs,
                  'nmod': nmod_subs,
                  'obl': obl_subs}

for key, value in deprel_mapping.items():
    for sub in value:
        dict_DEPREL[key + ':' + sub] = dict_DEPREL[key] + ' - ' + sub


# V2 REVISED TAGS https://universaldependencies.org/u/dep/all.html
# https://gist.github.com/nlothian/9240750
# from the Penn Treebank http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.9.8216&rep=rep1&type=pdf
# list of possible clausal tag values
dict_CLAUSALTAG = {
    'S': 'Sentence', \
    'SBAR': 'Subordinate clause - Clause introduced by a (possibly empty) subordinating conjunction', \
    # As Jack said, who would believe he did not cheat in the exam?
    'SBARQ': 'Direct question introduced by a wh-word or a wh-phrase', \
    # An inverted sentence (SINV) is a sentence in a normally
    #   subject-first language in which the predicate (verb)
    #   comes before the subject (noun).
    'SINV': 'Inverted declarative sentence', \
    # Example: Do you know you are driving with a flat tire?
    # Example: Would you like a drink?
    'SQ': 'Inverted yes/no question', \
    'ADJP': 'Adjective Phrase', \
    'ADVP': 'Adverb Phrase', \
    'CONJP': 'Conjunction Phrase', \
    'FRAG': 'Fragment', \
    'INTJ': 'Interjection', \
    'LST': 'List marker', \
    'NAC': 'Not a Constituent', \
    'NP': 'Noun Phrase', \
    'NX': 'Used within certain complex NPs to mark the head of the NP', \
    'PP': 'Prepositional Phrase', \
    'PRN': 'Parenthetical', \
    'PRT': 'Particle', \
    'QP': 'Quantifier Phrase', \
    'RRC': 'Reduced Relative Clause', \
    'UCP': 'Unlike Coordinated Phrase', \
    'VP': 'Verb Phrase', \
    'WHADJP': 'Wh-adjective Phrase', \
    'WHAVP': 'Wh-adverb Phrase', \
    'WHNP': 'Wh-noun Phrase', \
    'WHPP': 'Wh-noun Phrase', \
    'X': 'Unknown', \
    '0': 'Zero variant of "that" in subordinate clause', \
    }
