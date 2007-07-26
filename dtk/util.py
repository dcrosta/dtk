# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# All rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share to copy, distribute, display, and perform the work
#   * to Remix to make derivative works
# 
# Under the following conditions:
# 
#   * Attribution. You must attribute the work in the manner specified by the
#     author or licensor (but not in any way that suggests that they endorse you
#     or your use of the work).
#   * Share Alike. If you alter, transform, or build upon this work, you may
#     distribute the resulting work only under the same, similar or a compatible
#     license.
# 
#   * For any reuse or distribution, you must make clear to others the license
#     terms of this work.
#   * Any of the above conditions can be waived if you get permission from the
#     copyright holder.
#   * Apart from the remix rights granted under this license, nothing in this
#     license impairs or restricts the author's moral rights.
# 
# 
# Full text of the license can be found online:
# 
#   <http://creativecommons.org/licenses/by-sa/3.0/us/>


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
    unallocated = remaining

    sizes = []
    for (fixed, weight) in items:
        if fixed is not None:
            sizes.append( fixed )

        else:
            size = int(round( float(weight) / totalweight * remaining ))
            size = min(size, unallocated)
            sizes.append( size )
            
            unallocated -= size


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
                out[-1] = out[-1].strip()
                out.append(second)
                # i -= 1
    
                x = len(second) 
    
            else:
                out[-1] = out[-1].strip()
                out.append(word)
                x = l

        outlines.extend(out)

    return outlines

