import types

# more key codes (more in __init__.py)
ESC = 'esc'
TAB = 'tab'
NL = 'enter'
DEL = 'backspace'


def isprint(ch):
    if type(ch) == types.IntType:
        return ch >= 32 and ch < 127

    if len(ch) > 1:
        return False
