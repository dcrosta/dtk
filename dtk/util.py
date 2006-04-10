import re

class FlexSizer:
    """
    This utility class implements direction-agnostic
    flexible sizing of multiple items, taking into acount
    minimum and maximum sizes of the items, weight for
    allocating remaining space, as well as
    inter-item spacing. It is used, at least, by the
    Columns, Rows and ColumnListBox Drawables.
    """

    class SizeItem:
        def __init__(self, min, max, weight, **kwargs):
            self.min = min
            self.max = max
            if weight is None:
                self.weight = 1
            else:
                self.weight = weight

            # is set later
            self.size = None

            # set additional attributes
            for name in kwargs.keys():
                if name == 'min' or name == 'max' or name == 'weight' or name == 'size':
                    raise Exception, "attributes 'size', 'min', 'max' or 'weight' on SizeItem are reserved"
                self.__dict__[name] = kwargs[name]


    def __init__(self, spacing):
        self.items = []
        self.spacing = spacing

    def addItem(self, min, max, weight, **kwargs):
        """
        add an item (will become the last item). additional named
        arguments will be set as fields of the resulting SizeItem
        """
        self.items.append(self.SizeItem(min, max, weight, **kwargs))

    def calculate(self, available):
        """
        performs calculations on the items, and returns the list of
        items with the 'size' field set to the size that the item
        should be drawn at.
        """

        # the minimum required space
        required   = sum([item.min for item in self.items]) 
        available -= self.spacing * (len(self.items) - 1)

        if required > available:
            raise SizeException, "more space is required than available"

        # for dividing available space among the columns
        totalweight = float(sum([item.weight for item in self.items]))

        spaceleft  = available
        available -= required

        # calculate sizes in a 2-pass process:
        #
        # the first pass sizes all columns, making sure they're
        # at least their required minimum size, and then adding
        # from available space according to their weight. if
        # any column is greater than its maximum, it is scaled
        # back to its maximum, and the remainder added to the
        # 'extra' pool.
        #
        # in the second pass, if there is any space left to be
        # allocated from the 'extra' pool, it is divided amongst
        # the columns that are under their maximum, according to
        # their weights. 
        #
        # TODO: figure out a way to actually optimize this allocation
        # without subjecting to a possible infinite loop.

        for item in self.items:
            s = item.min + int(min(float(item.weight) / totalweight * available, spaceleft))
            if item.max is not None and s > item.max:
                s = item.max

            item.size = s

            spaceleft -= s


        if spaceleft > 0:
            available = spaceleft

            totalweight = float(sum([item.weight for item in self.items if item.size != item.max]))

            for item in self.items:
                if item.size == item.max:
                    continue

                s = int(min(float(item.weight) / totalweight * available, spaceleft))
                item.size += s
                
                spaceleft -= s


        # fudge the last item
        if spaceleft != 0:
            self.items[len(self.items) - 1].size += spaceleft 


        return self.items


class SizeException(Exception):
    """
    raised when the required size for an item or group of
    items is greater than the available space
    """


class BufferGappedString:
    """
    BufferGappedString implements an efficient string-like data
    structure to support the sorts of edits you'd expect to happen in
    an editable text field or text area -- that is, many small changes
    to a local area, then many small changes to a different local
    area. This implementation is based on suggestions by Chuck Groom
    in <http://bluemug.com/research/text.pdf>.
    """

    def __init__(self, contents = None, gapsize = 10):
        """
        Initializes the BufferGappedString to an empty string with a
        default gap size of 10
        """

        self.gapsize = 10

        if contents is not None:
            self.buf = list(str(contents))
            self.len = len(self.buf)

        else:
            # the first edit to the string will create the gap
            self.buf = []
            self.len = 0

    # the str interface (as of 2.4.2)

    def __add__(self):
        """
        x.__add__(y) <==> x+y
        """
        pass
    
    def __contains__(self):
        """
        x.__contains__(y) <==> y in x
        """
        pass
    
    def __eq__(self):
        """
        x.__eq__(y) <==> x==y
        """
        pass
    
    def __ge__(self):
        """
        x.__ge__(y) <==> x>=y
        """
        pass
    
    def __getattribute__(self):
        """
        x.__getattribute__('name') <==> x.name
        """
        pass
    
    def __getitem__(self):
        """
        x.__getitem__(y) <==> x[y]
        """
        pass
    
    def __getnewargs__(self):
        pass
    
    def __getslice__(self):
        """
        x.__getslice__(i, j) <==> x[i:j]
         
        Use of negative indices is not supported.
        """
        pass
    
    def __gt__(self):
        """
        x.__gt__(y) <==> x>y
        """
        pass
    
    def __hash__(self):
        """
        x.__hash__() <==> hash(x)
        """
        pass
    
    def __le__(self):
        """
        x.__le__(y) <==> x<=y
        """
        pass
    
    def __len__(self):
        """
        x.__len__() <==> len(x)
        """
        return self.len
    
    def __lt__(self):
        """
        x.__lt__(y) <==> x<y
        """
        pass
    
    def __mod__(self):
        """
        x.__mod__(y) <==> x%y
        """
        pass
    
    def __mul__(self):
        """
        x.__mul__(n) <==> x*n
        """
        pass
    
    def __ne__(self):
        """
        x.__ne__(y) <==> x!=y
        """
        pass
    
    def __repr__(self):
        """
        x.__repr__() <==> repr(x)
        """
        pass
    
    def __rmod__(self):
        """
        x.__rmod__(y) <==> y%x
        """
        pass
    
    def __rmul__(self):
        """
        x.__rmul__(n) <==> n*x
        """
        pass
    
    def __str__(self):
        """
        x.__str__() <==> str(x)
        """
        pass
    
    def capitalize(self):
        """
        S.capitalize() -> string
         
        Return a copy of the string S with only its first character
        capitalized.
        """
        pass
    
    def center(self):
        """
        S.center(width[, fillchar]) -> string
         
        Return S centered in a string of length width. Padding is
        done using the specified fill character (default is a space)
        """
        pass
    
    def count(self):
        """
        S.count(sub[, start[, end]]) -> int
         
        Return the number of occurrences of substring sub in string
        S[start:end].  Optional arguments start and end are
        interpreted as in slice notation.
        """
        pass
    
    def decode(self):
        """
        S.decode([encoding[,errors]]) -> object
         
        Decodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeDecodeError. Other possible values are 'ignore' and 'replace'
        as well as any other name registerd with codecs.register_error that is
        able to handle UnicodeDecodeErrors.
        """
        pass
    
    def encode(self):
        """
        S.encode([encoding[,errors]]) -> object
         
        Encodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeEncodeError. Other possible values are 'ignore', 'replace' and
        'xmlcharrefreplace' as well as any other name registered with
        codecs.register_error that is able to handle UnicodeEncodeErrors.
        """
        pass
    
    def endswith(self):
        """
        S.endswith(suffix[, start[, end]]) -> bool
         
        Return True if S ends with the specified suffix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        """
        pass
    
    def expandtabs(self):
        """
        S.expandtabs([tabsize]) -> string
         
        Return a copy of S where all tab characters are expanded using spaces.
        If tabsize is not given, a tab size of 8 characters is assumed.
        """
        pass
    
    def find(self):
        """
        S.find(sub [,start [,end]]) -> int
         
        Return the lowest index in S where substring sub is found,
        such that sub is contained within s[start,end].  Optional
        arguments start and end are interpreted as in slice notation.
         
        Return -1 on failure.
        """
        pass
    
    def index(self):
        """
        S.index(sub [,start [,end]]) -> int
         
        Like S.find() but raise ValueError when the substring is not found.
        """
        pass
    
    def isalnum(self):
        """
        S.isalnum() -> bool
         
        Return True if all characters in S are alphanumeric
        and there is at least one character in S, False otherwise.
        """
        pass
    
    def isalpha(self):
        """
        S.isalpha() -> bool
         
        Return True if all characters in S are alphabetic
        and there is at least one character in S, False otherwise.
        """
        pass
    
    def isdigit(self):
        """
        S.isdigit() -> bool
         
        Return True if all characters in S are digits
        and there is at least one character in S, False otherwise.
        """
        pass
    
    def islower(self):
        """
        S.islower() -> bool
         
        Return True if all cased characters in S are lowercase and there is
        at least one cased character in S, False otherwise.
        """
        pass
    
    def isspace(self):
        """
        S.isspace() -> bool
         
        Return True if all characters in S are whitespace
        and there is at least one character in S, False otherwise.
        """
        pass
    
    def istitle(self):
        """
        S.istitle() -> bool
         
        Return True if S is a titlecased string and there is at least one
        character in S, i.e. uppercase characters may only follow uncased
        characters and lowercase characters only cased ones. Return False
        otherwise.
        """
        pass
    
    def isupper(self):
        """
        S.isupper() -> bool
         
        Return True if all cased characters in S are uppercase and there is
        at least one cased character in S, False otherwise.
        """
        pass
    
    def join(self):
        """
        S.join(sequence) -> string
         
        Return a string which is the concatenation of the strings in the
        sequence.  The separator between elements is S.
        """
        pass
    
    def ljust(self):
        """
        S.ljust(width[, fillchar]) -> string
         
        Return S left justified in a string of length width. Padding is
        done using the specified fill character (default is a space).
        """
        pass
    
    def lower(self):
        """
        S.lower() -> string
         
        Return a copy of the string S converted to lowercase.
        """
        pass
    
    def lstrip(self):
        """
        S.lstrip([chars]) -> string or unicode
         
        Return a copy of the string S with leading whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is unicode, S will be converted to unicode before stripping
        """
        pass
    
    def replace(self):
        """
        S.replace (old, new[, count]) -> string
         
        Return a copy of string S with all occurrences of substring
        old replaced by new.  If the optional argument count is
        given, only the first count occurrences are replaced.
        """
        pass
    
    def rfind(self):
        """
        S.rfind(sub [,start [,end]]) -> int
         
        Return the highest index in S where substring sub is found,
        such that sub is contained within s[start,end].  Optional
        arguments start and end are interpreted as in slice notation.
         
        Return -1 on failure.
        """
        pass
    
    def rindex(self):
        """
        S.rindex(sub [,start [,end]]) -> int
         
        Like S.rfind() but raise ValueError when the substring is not found.
        """
        pass
    
    def rjust(self):
        """
        S.rjust(width[, fillchar]) -> string
         
        Return S right justified in a string of length width. Padding is
        done using the specified fill character (default is a space)
        """
        pass
    
    def rsplit(self):
        """
        S.rsplit([sep [,maxsplit]]) -> list of strings
         
        Return a list of the words in the string S, using sep as the
        delimiter string, starting at the end of the string and working
        to the front.  If maxsplit is given, at most maxsplit splits are
        done. If sep is not specified or is None, any whitespace string
        is a separator.
        """
        pass
    
    def rstrip(self):
        """
        S.rstrip([chars]) -> string or unicode
         
        Return a copy of the string S with trailing whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is unicode, S will be converted to unicode before stripping
        """
        pass
    
    def split(self):
        """
        S.split([sep [,maxsplit]]) -> list of strings
         
        Return a list of the words in the string S, using sep as the
        delimiter string.  If maxsplit is given, at most maxsplit
        splits are done. If sep is not specified or is None, any
        whitespace string is a separator.
        """
        pass
    
    def splitlines(self):
        """
        S.splitlines([keepends]) -> list of strings
         
        Return a list of the lines in S, breaking at line boundaries.
        Line breaks are not included in the resulting list unless keepends
        is given and true.
        """
        pass
    
    def startswith(self):
        """
        S.startswith(prefix[, start[, end]]) -> bool
         
        Return True if S starts with the specified prefix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        """
        pass
    
    def strip(self):
        """
        S.strip([chars]) -> string or unicode
         
        Return a copy of the string S with leading and trailing
        whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is unicode, S will be converted to unicode before stripping
        """
        pass
    
    def swapcase(self):
        """
        S.swapcase() -> string
         
        Return a copy of the string S with uppercase characters
        converted to lowercase and vice versa.
        """
        pass
    
    def title(self):
        """
        S.title() -> string
         
        Return a titlecased version of S, i.e. words start with uppercase
        characters, all remaining cased characters have lowercase.
        """
        pass
    
    def translate(self):
        """
        S.translate(table [,deletechars]) -> string
         
        Return a copy of the string S, where all characters occurring
        in the optional argument deletechars are removed, and the
        remaining characters have been mapped through the given
        translation table, which must be a string of length 256.
        """
        pass
    
    def upper(self):
        """
        S.upper() -> string
         
        Return a copy of the string S converted to uppercase.
        """
        pass
    
    def zfill(self):
        """
        S.zfill(width) -> string
         
        Pad a numeric string S with zeros on the left, to fill a field
        of the specified width.  The string S is never truncated.
        """
        pass

def wrap(line, width):
    """
    Wrap a line of text to the given width. Whitespace is allowed to
    "dangle" over the edge, and words are split at hyphens.

    @param line: the long line of text
    @type  line: string

    @param width: the width to wrap to
    @type  width: integer

    @return: a list of strings suitable to be printed into an area
        width wide
    @rtype: list of strings
    """
    out = ['']
    x = 0

    words = re.split('([\s]*)', line)

    # allow hyphens to split
    newwords = []
    for word in words:
        split = word.split('-')
        
        for part in split[:-1]:
            newwords.append('%s-' % part)
        newwords.append(split[-1])

            
    words = newwords

    
    for i in range(len(words)):
        word = words[i]

        l = len(word)
        iswhitespace = (re.match('\s+$', word) is not None)

        if x + l <= width or iswhitespace:
            out[-1] += word
            x += l

        # this case needs to be made smarter
        elif l > width:
            # split the word in half
            first  = word[:width - x]
            second = word[width - x:]

            out[-1] += first
            out.append(second)
            # i -= 1

            x = len(second) 

        else:
            out.append(word)
            x = l

    return out

