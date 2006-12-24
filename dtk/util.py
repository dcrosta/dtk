import re


class SizeException(Exception):
    pass


def flexSize(items, space):
    """
    accepts items as list of (fixedsize, weight). if an
    item has a fixed size, it will always be that size;
    if not, the available space is allocated among items
    according to their weight

    @param items: list of tuples as (fixed size, weight).
        to use weight, set fixed size to None
    @type  items: list

    @param space: amount of space to allocate
    @type  space: int
    """
    required = sum( [a for (a, b) in items if a is not None] )
    totalweight = float( sum( [b for (a, b) in items if a is None] ) )

    if required > space or (required == space and totalweight != 0):
        raise SizeException, "more space is required than available"

    remaining = space - required

    sizes = []
    for (fixed, weight) in items:
        if fixed is not None:
            sizes.append( fixed )

        else:
            sizes.append( int(round( float(weight) / totalweight * remaining )) )


    if sum( sizes ) != space:
        raise SizeException, "sum of allocated sizes != available space: %d != %d" % (sum(sizes), space)

    return sizes


def wrap(line, width):
    """
    Wrap a line of text to the given width. Whitespace is allowed to
    "dangle" over the edge, and words are split at hyphens.

    @param line: the long line of text
    @type  line: string

    @param width: the width to wrap to
    @type  width: int

    @return: a list of strings suitable to be printed into an area
        width wide
    @rtype: list of strings
    """

    lines = line.split('\n')
    outlines = []

    for line in lines:
        out = ['']
        x = 0

        words = re.split('(\s*)', line)
    
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
            iswhitespace = (re.match('\s*$', word) is not None)
    
            if x + l <= width or iswhitespace:
                out[-1] += word
                x += l
    
            # this case needs to be made smarter
            elif l > width:
                # split the word in two
                first  = word[:width - x]
                second = word[width - x:]
    
                out[-1] += first
                out.append(second)
                # i -= 1
    
                x = len(second) 
    
            else:
                out.append(word)
                x = l

        outlines.extend(out)

    return outlines

