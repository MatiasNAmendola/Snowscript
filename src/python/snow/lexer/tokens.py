import re
from functools import wraps

from error import raise_syntax_error
import tokenize
from ply import lex

MODES = {'PHP':0, 'HTML': 1}
MODE = 0

tokens = ['ABSTRACT', 'AMPER', 'AND', 'AND_EQUAL', 'ARRAY', 'AT', 'BACKQUOTE',
     'BAND', 'BLEFT', 'BNOT', 'BOOL', 'BOR', 'BOX', 'BREAK', 'BRIGHT', 'BXOR',
     'CALLABLE', 'CASE', 'CATCH', 'CIRCUMFLEX', 'CLASS', 'CLASS_NAME', 'CLONE',
     'COLON', 'COMMA', 'COMMENT', 'COMMENT_MULTILINE', 'CONCAT_EQUAL', 'CONST', 
     'CONSTANT_NAME',
     'DEC', 'DECLARE', 'DEFAULT', 'DIE', 'DIV_EQUAL', 'DOUBLE_DOT', 'DOT',
     'DOUBLE_COLON', 'DOWNTO', 'ECHO', 'ELIF', 'ELSE', 'EMPTY', 'END',
     'EQUAL', 'ESCAPE', 'EXIT', 'EXTENDS', 'FALLTHRU', 'FALSE', 'FINAL',
     'FLOAT', 'FN', 'FOR', 'GLOBAL', 'GREATER', 'IF', 'IMPLEMENTS', 'IN',
     'INC', 'INCLUDE', 'INCLUDE_ONCE', 'INLINE_HTML', 'INNER_RETURN',
     'INSIDE_COMMENT', 'INT', 'INTERFACE', 'ISA', 'ISSET', 'IS_EQUAL',
     'IS_GREATER_OR_EQUAL', 'IS_IDENTICAL', 'IS_NOT_EQUAL', 'IS_NOT_IDENTICAL',
     'IS_SMALLER_OR_EQUAL', 'LBRACE', 'LESS', 'LIST', 'LPAR', 'LSQB', 'MINUS',
     'MINUS_EQUAL', 'MOD', 'MOD_EQUAL', 'MUL_EQUAL', 'NAMESPACE', 'NEW',
     'NEXT', 'NOT', 'NULL', 'OBJECT', 'OR', 'OR_EQUAL', 'PASS', 'PERCENT',
     'PIPE', 'PLUS', 'PLUS_EQUAL', 'POW', 'PRINT', 'PRIVATE', 'PROTECTED',
     'PUBLIC', 'RBRACE', 'RECEIVER', 'REQUIRE', 'REQUIRE_ONCE', 'RETURN',
     'RPAR', 'RSQB', 'SEMI', 'SL', 'SLASH', 'SL_EQUAL', 'SR', 'SR_EQUAL',
     'STAR', 'STATIC', 'STRINGTYPE', 'STRING_WITH_CONCAT', 'SWITCH', 'THROW',
     'TILDE', 'TO', 'TRAIT', 'TRUE', 'TRY', 'UNSET', 'USE', 'VARIABLE_NAME',
     'WHEN', 'WHILE', 'XOR', 'XOR_EQUAL', '_AND_', '_OR_', 'STEP',
     'DOUBLE_ARROW', 'DOUBLE_QUESTION_MARK', 'QUESTION_MARK', 'THEN', 
     'STRING_DOUBLE', 'STRING_SINGLE', 'PARENT',
]

token_groups = {
    # Keywords.
    'kwd': ['ABSTRACT', 'AND', 'ARRAY', 'BAND', 'BLEFT', 'BNOT', 
            'BOR', 'BOX', 'BREAK', 'BRIGHT', 'BXOR', 'CALLABLE', 
            'CASE', 'CATCH', 'CLASS', 'CLONE', 
            'CONST', 'DECLARE', 'DEFAULT', 'DIE', 'DOWNTO', 
            'ECHO', 'ELIF', 'ELSE', 'EMPTY', 'END', 'ESCAPE', 'EXIT', 
            'EXTENDS', 'FALLTHRU', 'FINAL', 'FN', 'FOR', 
            'GLOBAL', 'IF', 'IMPLEMENTS', 'IN', 'INCLUDE', 'INCLUDE_ONCE', 
            'INTERFACE', 'ISA', 
            'ISSET', 'LIST', 'MOD', 'MOD_EQUAL', 
            'NAMESPACE', 'NEW', 'NEXT', 'NOT', 'OR', 
            'OR_EQUAL', 'PASS', 'PRINT', 'PRIVATE', 'PROTECTED', 'PUBLIC', 
            'REQUIRE', 'REQUIRE_ONCE', 
            'STATIC', 'SWITCH', 'THROW', 
            'TO', 'TRAIT', 'TRUE', 'TRY', 'UNSET', 'USE', 
            'WHEN', 'WHILE', 'XOR', 'XOR_EQUAL', '_AND_', '_OR_', 'STEP',
            'DOUBLE_QUESTION_MARK', 'QUESTION_MARK', 'THEN', 'PARENT'
            ],
    # Strings.
    'str': ['INLINE_HTML', 'STRING_WITH_CONCAT', 'STRING_DOUBLE', 'STRING_SINGLE'],
    # Comments.
    'com': ['INSIDE_COMMENT'],
    # Types.
    'type': ['FLOAT', 'BOOL', 'INT', 'NULL', 'OBJECT', 'STRINGTYPE'],
    # Litteral values.
    'lit': ['FALSE', 'TRUE', 'NUMBER'],
    # Plain text.
    'pln': ['CLASS_NAME', 'CONSTANT_NAME', 'VARIABLE_NAME', 'WS', 'NAME', 
            'NEWLINE'],
    # Punctuation.
    'pun': ['INC', 'DEC', 'IS_IDENTICAL', 'IS_NOT_IDENTICAL', 'IS_EQUAL',
            'IS_NOT_EQUAL', 't_IS_SMALLER_OR_EQUAL', 'IS_GREATER_OR_EQUAL',
            'PLUS_EQUAL', 'MINUS_EQUAL', 'MUL_EQUAL', 'DIV_EQUAL',
            'CONCAT_EQUAL', 'POW', 'RETURN', 'INNER_RETURN', 'RECEIVER',
            'DOUBLE_COLON', 'COLON', 'COMMA', 'SEMI', 'PLUS', 'MINUS', 'STAR',
            'SLASH', 'PIPE', 'AMPER', 'LESS', 'GREATER', 'EQUAL', 'DOUBLE_DOT', 'DOT',
            'PERCENT', 'BACKQUOTE', 'CIRCUMFLEX', 'TILDE', 'AT', 'LPAR',
            'RPAR', 'LBRACE', 'RBRACE', 'LSQB', 'RSQB', 'DOUBLE_ARROW', 
            'AND_EQUAL', 'COMMENT', 'COMMENT_MULTILINE', 'IS_SMALLER_OR_EQUAL', 'SL', 'SL_EQUAL', 
            'SR', 'SR_EQUAL'],
}

RESERVED = dict([(t.lower(), t) for t in tokens])
RESERVED['str'] = 'STRINGTYPE'
del RESERVED['stringtype']

# The presence of one of these may force an indentation on the next.
INDENTATION_TRIGGERS = ('IF', 'ELSE', 'ELIF', 'FOR', 'SWITCH', 'CASE', 'WHILE',
    'DEFAULT', 'FN', 'CLASS', 'INTERFACE', 'TRAIT', 'TRY', 'CATCH'
    # 'STATIC', 'PRIVATE', 'CONST', 'PUBLIC', 'PROTECTED',
)

# The supported casts.
CASTS = ('ARRAY', 'BOOL', 'FLOAT', 'INT', 'OBJECT', 'STRINGTYPE', )

# Keywords where parenthensis can be omitted.
MISSING_PARENTHESIS = ('IF', 'ELIF', 'FOR', 'SWITCH', 'WHILE', 'CATCH', 'CASE')

# For some super weird reason, having this line breaks everything. Hmm :)
SYMBOLIC = token_groups['pun']

## Token definitions ##
t_INC = r'\+\+'
t_DEC = r'\-\-'
t_IS_IDENTICAL = r'\=\=\='
t_IS_NOT_IDENTICAL = r'\!\=\='
t_IS_EQUAL = r'\=\='
t_IS_NOT_EQUAL = r'\!\='
t_IS_SMALLER_OR_EQUAL = r'\<\='
t_IS_GREATER_OR_EQUAL = r'\>\='
t_PLUS_EQUAL = r'\+\='
t_MINUS_EQUAL = r'\-\='
t_MUL_EQUAL = r'\*\='
t_DIV_EQUAL = r'\/\='
t_CONCAT_EQUAL = r'\%\='
t_POW = r'\*\*'
t_RETURN = r'\<\-'
t_INNER_RETURN = r'\<\-\-'
t_RECEIVER = r'\-\>'
t_DOUBLE_DOT = r'\.\.'
t_DOUBLE_COLON = r'\:\:'
t_DOUBLE_QUESTION_MARK = r'\?\?'
t_COLON = r'\:'
t_COMMA = r'\,'
t_SEMI = r'\;'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_STAR = r'\*'
t_SLASH = r'\/'
t_PIPE = r'\|'
t_AMPER = r'\&'
t_LESS = r'\<'
t_GREATER = r'\>'
t_EQUAL = r'\='
t_DOT = r'\.'
t_PERCENT = r'\%'
t_BACKQUOTE = r'\`'
t_CIRCUMFLEX = r'\^'
t_TILDE = r'\~'
t_AT = r'\@'
t_QUESTION_MARK = r'\?'


def t_COMMENT_MULTILINE(t):
    r"\#\#\#"
    t.lexer.push_state('MULTILINECOMMENT')

def t_MULTILINECOMMENT_END(t):
    r"\#\#\#"
    t.lexer.pop_state()

def t_MULTILINECOMMENT_INSIDE(t):
    r"[^\#]+"

def t_MULTILINECOMMENT_ESCAPE(t):
    r"\#"

def t_MULTILINECOMMENT_error(t):
    print t
    raise_syntax_error("invalid syntax", t)

def t_comment(t):
    r"[ ]?\#[^\n]*"
    
def t_MOD_EQUAL(t):
    r'mod\='
    t.type = RESERVED.get(t.value, "MOD_EQUAL")
    return t


def t_SL_EQUAL(t):
    r'bleft\='
    t.type = RESERVED.get(t.value, "SL_EQUAL")
    return t


def t_SR_EQUAL(t):
    r'bright\='
    t.type = RESERVED.get(t.value, "SR_EQUAL")
    return t


def t_AND_EQUAL(t):
    r'band\='
    t.type = RESERVED.get(t.value, "AND_EQUAL")
    return t


def t_OR_EQUAL(t):
    r'bor\='
    t.type = RESERVED.get(t.value, "OR_EQUAL")
    return t


def t_XOR_EQUAL(t):
    r'bxor\='
    t.type = RESERVED.get(t.value, "XOR_EQUAL")
    return t


def t_SL(t):
    r'bleft\='
    t.type = RESERVED.get(t.value, "SL")
    return t


def t_SR(t):
    r'bright\='
    t.type = RESERVED.get(t.value, "SR")
    return t

MAGIC_CONSTS = (
    '__CLASS',
    '__DIR',
    '__FILE',
    '__FUNCTION',
    '__LINE',
    '__METHOD',
    '__NAMESPACE',
    '__TRAIT',
)

GLOBALS = (
    '__SERVER',
    '__GET',
    '__POST',
    '__FILES',
    '__COOKIE',
    '__SESSION',
    '__REQUEST',
    '__ENV',
)
def t_VARIABLE_NAME(t):
    r"[_]*[a-z][a-zA-Z0-9_]*"
    t.type = RESERVED.get(t.value, "NAME")
    return t


def t_CLASS_NAME(t):
    r"[A-Z_][a-zA-Z0-9_]*"
    if t.value == t.value.upper() and len(t.value) > 1:
        if t.value in MAGIC_CONSTS:
            t.value += "__"
            t.type = "CONSTANT_NAME"
        elif t.value == "__GLOBALS":
            t.value = "GLOBALS"
            t.type = "NAME"
        elif t.value in GLOBALS:
            t.value = t.value[1:]
            t.type = "NAME"
        else:
            t.type = RESERVED.get(t.value, "NAME")
    return t


def t_CONSTANT_NAME(t):
    "\![A-Z_][A-Z0-9_]*"
    t.value = t.value[1:]
    return t


def t_error(t):
    print t
    raise_syntax_error("invalid syntax", t)


# Whitespace tokens.

def t_WS(t):
    r" [ \t\f]+ "
    value = t.value

    # A formfeed character may be present at the start of the
    # line; it will be ignored for the indentation calculations
    # above. Formfeed characters occurring elsewhere in the
    # leading whitespace have an undefined effect (for instance,
    # they may reset the space count to zero).
    value = value.rsplit("\f", 1)[-1]

    # First, tabs are replaced (from left to right) by one to eight
    # spaces such that the total number of characters up to and
    # including the replacement is a multiple of eight (this is
    # intended to be the same rule as used by Unix). The total number
    # of spaces preceding the first non-blank character then
    # determines the line's indentation. Indentation cannot be split
    # over multiple physical lines using backslashes; the whitespace
    # up to the first backslash determines the indentation.
    pos = 0
    while 1:
        pos = value.find("\t")
        if pos == -1:
            break
        n = 8 - (pos % 8)
        value = value[:pos] + " " * n + value[pos + 1:]
    
    if MODE == MODES['PHP']:
        if t.lexer.at_line_start and t.lexer.bracket_level == 0:
            return t
    elif MODE == MODES['HTML']:
        return t
    else:
        raise NotImplementedError()

def t_escaped_newline(t):
    r"\\\n"
    # string continuation - ignored beyond the tokenizer level.
    t.type = "STRING_CONTINUE"
    # Raw strings don't escape the newline.
    assert not t.lexer.is_raw, "only occurs outside of quoted strings"
    t.lexer.lineno += 1


def t_newline(t):
    r"\n+"
    # Don't return newlines while I'm inside of ()s.
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    if MODE == MODES['PHP']:
        if t.lexer.bracket_level == 0:
            return t
    elif MODE == MODES['HTML']:
        return t
    else:
        raise NotImplementedError()

# Numbers. #


@lex.TOKEN(tokenize.Imagnumber)
def t_IMAG_NUMBER(t):
    # The NUMBER tokens return a 2-ple of (value, original string)-
    # The original string can be used to get the span of the original
    # token and to provide better round-tripping.
    #
    # imaginary numbers in Python are represented with floats,
    #   (1j).imag is represented the same as (1.0j).imag -- with a float.
    t.type = "NUMBER"
    t.value = (float(t.value[:-1]) * 1j, t.value)
    return t


@lex.TOKEN(tokenize.Floatnumber)
def t_FLOAT_NUMBER(t):
    # Then check for floats (must have a ".")
    t.type = "NUMBER"
    t.value = (float(t.value), t.value)
    return t


def t_HEX_NUMBER(t):
    r"0[xX][0-9a-fA-F]+[lL]?"
    # In the following I use 'long' to make the actual type match the
    # results from the compiler module.  Otherwise there's no need for it.
    #
    # Python allows "0x", but in reading python-dev it looks like this was
    # removed in 2.6/3.0.  I don't allow it.
    t.type = "NUMBER"
    value = t.value
    if value[-1] in "lL":
        value = value[:-1]
        f = long
    else:
        f = int
    t.value = (f(value, 16), t.value)
    return t


def t_OCT_NUMBER(t):
    r"0[0-7]*[lL]?"
    t.type = "NUMBER"
    value = t.value
    if value[-1] in "lL":
        value = value[:-1]
        f = long
    else:
        f = int
    t.value = (f(value, 8), t.value)
    return t


def t_DEC_NUMBER(t):
    r"[1-9][0-9]*[lL]?"
    t.type = "NUMBER"
    value = t.value
    if value[-1] in "lL":
        value = value[:-1]
        f = long
    else:
        f = int
    t.value = (f(value, 10), t.value)
    return t

# Brackets. #


def t_LPAR(t):
    r'\('
    t.lexer.bracket_level += 1
    return t


def t_RPAR(t):
    r'\)'
    t.lexer.bracket_level -= 1
    return t


def t_LBRACE(t):
    r'\{'
    t.lexer.bracket_level += 1
    return t


def t_RBRACE(t):
    r'\}'
    t.lexer.bracket_level -= 1
    return t


def t_LSQB(t):
    r'\['
    t.lexer.bracket_level += 1
    t.lexer.push_state('INSIDEARRAY')
    return t


def t_RSQB(t):
    r'\]'
    t.lexer.bracket_level -= 1
    t.lexer.pop_state()
    return t


def t_INSIDEARRAY_COLON(t):
    r'\:'
    t.type = 'DOUBLE_ARROW'
    return t

# Strings. #


def html_mode_string(f):
    """
    Decorator that returns a unaltered string token if the mode is set to
    HTML, otherwise keeps the original return.
    """
    if MODE == MODES['PHP']:
       return f
    if MODE != MODES['HTML']:
        raise NotImplementedError()
    
    @wraps(f)
    def _(t):
        orig_value = t.value
        t2 = f(t)
        t.type = "STRING"
        t.value = orig_value
        return t
    
    return _
    
INDENTION_CHARS = "    "

def add_to_string(t, value):
    """Adds a value to the lexers string_content variable."""
    # For double quoted strings, remove the whitespace on each beginning line
    # matching one more than the current indention level.
    if t.lexer.current_state() in ('INDOUBLEQUOTEDSTRING', 'INTRIPPLEDOUBLEQUOTEDSTRING'):
        indention = INDENTION_CHARS * (t.lexer.indent_level+1)
        value = value.replace("\n%s" % indention, "\n")
    t.lexer.string_content += value 


def get_string_token(t, type='STRING'):
    """Returns a string token with the value of the lexers
    string_content variable which is then reset to ''."""
    # Remove escaped linebreaks.
    t.value = t.lexer.string_content.replace("\\\n", "")
    t.lexer.string_content = ''
    t.type = type
    return t


def snow_begin(t):
    # Going into Snow mode. Return collected strings if any.
    t.lexer.push_state('SNOWINANYDOUBLEQUOTEDSTRING')
    if t.lexer.string_content:
        return get_string_token(t, type='STRING_WITH_CONCAT')

def string_begin(t, to_state, string_type):
    t.lexer.string_content = ''
    t.lexer.string_type = string_type
    t.lexer.push_state(to_state)
    t.lexer.starting_string_token = t


def string_end(t, from_state):
    t.lexpos = t.lexer.starting_string_token.lexpos
    t.lineno = t.lexer.starting_string_token.lineno
    t.lexer.pop_state()
    return get_string_token(t, t.lexer.string_type)


def add_escape(t):
    add_to_string(t, t.value[1] if len(t.value) > 1 else t.value[0])

## Tripple doublequoted string

@html_mode_string
def t_TRIPPLE_string_begin(t):
    r'"""'
    string_begin(t, 'INTRIPPLEDOUBLEQUOTEDSTRING', 'STRING_DOUBLE')

@html_mode_string
def t_INTRIPPLEDOUBLEQUOTEDSTRING_ESCAPE(t):
    r'(\\")|(\\{)|(\\)'
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_escape(t)

@html_mode_string
def t_INTRIPPLEDOUBLEQUOTEDSTRING_STRING(t):
    r'[^{"\\]+'
    # All that are normal string chars.
    add_to_string(t, t.value)

@html_mode_string
def t_INTRIPPLEDOUBLEQUOTEDSTRING_STRING_END(t):
        r'"""'
        t.lexer.string_content = t.lexer.string_content.replace('"', r'\"')
        return string_end(t, 'INTRIPPLEDOUBLEQUOTEDSTRING')

@html_mode_string
def t_INTRIPPLEDOUBLEQUOTEDSTRING_SINGLEQUOTE(t):
    r'"'
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_to_string(t, t.value)

@html_mode_string
def t_INTRIPPLEDOUBLEQUOTEDSTRING_SNOW_BEGIN(t):
    r"{"
    return snow_begin(t)


def t_INTRIPPLEDOUBLEQUOTEDSTRING_error(t):
    print t
    raise_syntax_error("invalid syntax", t)

@html_mode_string
def t_string_begin(t):
    r'"'
    ## Single doublequoted string.
    string_begin(t, 'INDOUBLEQUOTEDSTRING', 'STRING_DOUBLE')

@html_mode_string
def t_INDOUBLEQUOTEDSTRING_ESCAPE(t):
    r'(\\")|(\\{)|(\\)'
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_escape(t)

@html_mode_string
def t_INDOUBLEQUOTEDSTRING_STRING(t):
        r'[^{"\\]+'
        # All that are normal string chars.
        add_to_string(t, t.value)

@html_mode_string
def t_INDOUBLEQUOTEDSTRING_STRING_END(t):
        r'"'
        return string_end(t, 'INDOUBLEQUOTEDSTRING')

@html_mode_string
def t_INDOUBLEQUOTEDSTRING_SNOW_BEGIN(t):
        r"{"
        return snow_begin(t)


def t_INDOUBLEQUOTEDSTRING_error(t):
    print t
    raise_syntax_error("invalid syntax", t)


## Tripple Single singlequoted string.


def t_TRIPPLE_SINGLEQUOTED_STRING_BEGIN(t):
    r"'''"
    string_begin(t, 'INTRIPPLESINGLEQUOTEDSTRING', 'STRING_SINGLE')


def t_INTRIPPLESINGLEQUOTEDSTRING_ESCAPE(t):
    r"(\\')|(\\)"
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_escape(t)


def t_INTRIPPLESINGLEQUOTEDSTRING_STRING(t):
    r"[^'\\]+"
    # All that are normal string chars.
    add_to_string(t, t.value)


def t_INTRIPPLESINGLEQUOTEDSTRING_STRING_END(t):
    r"'''"
    return string_end(t, 'INTRIPPLESINGLEQUOTEDSTRING')


def t_INTRIPPLESINGLEQUOTEDSTRING_SINGLEQUOTE(t):
    r"'"
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_to_string(t, t.value)


def t_INTRIPPLESINGLEQUOTEDSTRING_error(t):
    raise_syntax_error("invalid syntax", t)


## Single singlequoted string.


def t_SINGLEQUOTED_STRING_BEGIN(t):
    r"'"
    string_begin(t, 'INSINGLEQUOTEDSTRING', 'STRING_SINGLE')


def t_INSINGLEQUOTEDSTRING_ESCAPE(t):
    r"(\\')|(\\)"
    # Matches an escaped " or { or a single \ as these should count as a normal
    # string char.
    add_escape(t)


def t_INSINGLEQUOTEDSTRING_STRING(t):
        r"[^'\\]+"
        # All that are normal string chars.
        add_to_string(t, t.value)


def t_INSINGLEQUOTEDSTRING_STRING_END(t):
        r"'"
        return string_end(t, 'INSINGLEQUOTEDSTRING')


def t_INSINGLEQUOTEDSTRING_error(t):
    print t
    raise_syntax_error("invalid syntax", t)

## Snow end

@html_mode_string
def t_SNOWINANYDOUBLEQUOTEDSTRING_SNOW_END(t):
    r"}"
    t.lexer.starting_string_token = t
    # Pop state back to INDOUBLEQUOTEDSTRING.
    t.lexer.pop_state()
    t.type = "PERCENT"
    t.value = "%"
    return t
