import sublime

from .base import EnhancedSnippetBase

from random import randrange
from textwrap import wrap

# Port of https://github.com/npmgod/Corporate-Ipsum

_split_chance = 75;


## ----------------------------------------------------------------------------


words = {
    'adverbs': [
        'appropriately', 'assertively', 'authoritatively', 'collaboratively',
        'compellingly', 'competently', 'completely', 'continually',
        'conveniently', 'credibly', 'distinctively', 'dramatically',
        'dynamically', 'efficiently', 'energistically', 'enthusiastically',
        'fungibly', 'globally', 'holisticly', 'interactively', 'intrinsically',
        'monotonectally', 'objectively', 'phosfluorescently', 'proactively',
        'professionally', 'progressively', 'quickly', 'rapidiously',
        'seamlessly', 'synergistically', 'uniquely'
    ],

    'verbs': [
        'actualize', 'administrate', 'aggregate', 'architect', 'benchmark',
        'brand', 'build', 'cloudify', 'communicate', 'conceptualize',
        'coordinate', 'create', 'cultivate', 'customize', 'deliver', 'deploy',
        'develop', 'dinintermediate disseminate', 'drive', 'embrace',
        'e-enable', 'empower', 'enable', 'engage', 'engineer', 'enhance',
        'envisioneer', 'evisculate', 'evolve', 'expedite', 'exploit', 'extend',
        'fabricate', 'facilitate', 'fashion', 'formulate', 'foster',
        'generate', 'grow', 'harness', 'impact', 'implement', 'incentivize',
        'incubate', 'initiate', 'innovate', 'integrate', 'iterate',
        'leverage existing', "leverage other's", 'maintain', 'matrix',
        'maximize', 'mesh', 'monetize', 'morph', 'myocardinate', 'negotiate',
        'network', 'optimize', 'orchestrate', 'parallel task', 'plagiarize',
        'pontificate', 'predominate', 'procrastinate', 'productivate',
        'productize', 'promote', 'provide access to', 'pursue',
        'recaptiualize', 'reconceptualize', 'redefine', 're-engineer',
        'reintermediate', 'reinvent', 'repurpose', 'restore', 'revolutionize',
        'right-shore', 'scale', 'seize', 'simplify', 'strategize',
        'streamline', 'supply', 'syndicate', 'synergize', 'synthesize',
        'target', 'transform', 'transition', 'underwhelm', 'unleash',
        'utilize', 'visualize', 'whiteboard'
    ],

    'adjectives': [
        '24/7', '24/365', 'accurate', 'adaptive', 'agile', 'alternative',
        'an expanded array of', 'B2B', 'B2C', 'backend', 'backward-compatible',
        'best-of-breed', 'bleeding-edge', 'bricks-and-clicks', 'business',
        'clicks-and-mortar', 'client-based', 'client-centered',
        'client-centric', 'client-focused', 'cloud-based', 'cloud-centric',
        'cloudified', 'collaborative', 'compelling', 'competitive',
        'cooperative', 'corporate', 'cost effective', 'covalent',
        'cross functional', 'cross-media', 'cross-platform', 'cross-unit',
        'customer directed', 'customized', 'cutting-edge', 'distinctive',
        'distributed',
        'diverse', 'dynamic', 'e-business', 'economically sound', 'effective',
        'efficient', 'elastic', 'emerging', 'empowered', 'enabled',
        'end-to-end', 'enterprise', 'enterprise-wide', 'equity invested',
        'error-free', 'ethical', 'excellent', 'exceptional', 'extensible',
        'extensive', 'flexible', 'focused', 'frictionless', 'front-end',
        'fully researched', 'fully tested', 'functional', 'functionalized',
        'fungible', 'future-proof', 'global', 'go forward', 'goal-oriented',
        'granular', 'high standards in', 'high-payoff', 'hyperscale',
        'high-quality', 'highly efficient', 'holistic', 'impactful',
        'inexpensive', 'innovative', 'installed base', 'integrated',
        'interactive', 'interdependent', 'intermandated', 'interoperable',
        'intuitive', 'just in time', 'leading-edge', 'leveraged',
        'long-term high-impact', 'low-risk high-yield', 'magnetic',
        'maintainable', 'market positioning', 'market-driven',
        'mission-critical', 'multidisciplinary', 'multifunctional',
        'multimedia based', 'next-generation', 'on-demand', 'one-to-one',
        'open-source', 'optimal', 'orthogonal', 'out-of-the-box', 'pandemic',
        'parallel', 'performance based', 'plug-and-play', 'premier', 'premium',
        'principle-centered', 'proactive', 'process-centric', 'professional',
        'progressive', 'prospective', 'quality', 'real-time', 'reliable',
        'resource-sucking', 'resource-maximizing', 'resource-leveling',
        'revolutionary', 'robust', 'scalable', 'seamless', 'stand-alone',
        'standardized', 'standards compliant', 'state of the art', 'sticky',
        'strategic', 'superior', 'sustainable', 'synergistic', 'tactical',
        'team building', 'team driven', 'technically sound', 'timely',
        'top-line', 'transparent', 'turnkey', 'ubiquitous', 'unique',
        'user-centric', 'user friendly', 'value-added', 'vertical', 'viral',
        'virtual', 'visionary', 'web-enabled', 'wireless', 'world-class',
        'worldwide'
    ],

    'nouns': [
        'action items', 'alignments', 'applications', 'architectures',
        'bandwidth', 'benefits', 'best practices', 'catalysts for change',
        'channels', 'clouds', 'collaboration and idea-sharing', 'communities',
        'content', 'convergence', 'core competencies', 'customer service',
        'data', 'deliverables', 'e-business', 'e-commerce', 'e-markets',
        'e-tailers', 'e-services', 'experiences', 'expertise',
        'functionalities', 'fungibility', 'growth strategies', 'human capital',
        'ideas', 'imperatives', 'infomediaries', 'information',
        'infrastructures', 'initiatives', 'innovation', 'intellectual capital',
        'interfaces', 'internal or "organic" sources', 'leadership',
        'leadership skills', 'manufactured products', 'markets', 'materials',
        'meta-services', 'methodologies', 'methods of empowerment', 'metrics',
        'mindshare', 'models', 'networks', 'niches', 'niche markets', 'nosql',
        'opportunities', '"outside the box" thinking', 'outsourcing',
        'paradigms', 'partnerships', 'platforms', 'portals', 'potentialities',
        'process improvements', 'processes', 'products', 'quality vectors',
        'relationships', 'resources', 'results', 'ROI', 'scenarios', 'schemas',
        'scrums', 'services', 'solutions', 'sources', 'sprints',
        'strategic theme areas', 'storage', 'supply chains', 'synergy',
        'systems', 'technologies', 'technology', 'testing procedures',
        'total linkage', 'users', 'value', 'vortals', 'web-readiness',
        'web services', 'wins', 'virtualization'
    ],

    'transitionals': ['and', 'then', 'to']
}


## ----------------------------------------------------------------------------


def get_word(word_type):
    """
    Randomly select a word of the provided type from the list of known words
    of that type.
    """
    word_list = words[word_type];
    return word_list[randrange(len(word_list))];


# Generating the ipsum
def create_ipsum(length=3):
    string = '';
    last_was_split = False;

    for i in range(length):
        is_full_sentence = True if randrange(100) < _split_chance else False
        adverb = get_word('adverbs')
        verb = get_word('verbs')
        adjective = get_word('adjectives')
        noun = get_word('nouns')

        if not last_was_split:
            adverb = adverb.capitalize()

        string += f'{adverb} {verb} {adjective} {noun}'

        if is_full_sentence and i != length - 1:
            transitional = get_word('transitionals')
            string += f', {transitional} '
            last_was_split = True
        else:
            string += '. '
            last_was_split = False

    return string


## ----------------------------------------------------------------------------


class InsertBuzzwordSnippet(EnhancedSnippetBase):
    """
    This snippet enhancement class provides a BUZZWORD snippet that behaves as
    a lorem snippet, but generates a randomly generated corporate lorem ipsum
    string.
    """
    def variable_name(self):
        return 'BUZZWORD'


    def variables(self, content):
        """
        The only variable that we support is a BUZZWORD, which inserts a
        corporate buzzword lorem into the snippet.

        This will potentially rewrite the content of the snippet and export
        many variables, once for each of the mentions of the variable in the
        snippet, so that there can be multiple insertions.
        """
        variables = {}

        def add_variable(match):
            fmt = match.group(1)

            try:
                count = int(fmt[1:]) or 1
            except:
                count = 1

            var = f"BUZZWORD_{len(variables)}"
            variables[var] = "\n".join(wrap(create_ipsum(count), width=80))

            return f'${{{var}}}'

        content = self.regex.sub(add_variable, content)
        return variables, content



## ----------------------------------------------------------------------------
