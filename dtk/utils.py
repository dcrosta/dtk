
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
