from Drawable import Drawable


class Container(Drawable):

    def __init__(self, parent, name):
        Drawable.__init__(self, parent, name)

        # this is all we keep track of
        self.children = []

    def register(self, drawable):
        """
        keep track of our children
        """
        self.children.append(drawable)
        self.parent.register(drawable)

    def setSize(self, y, x, h, w):
        """
        um... this is a generic container, so we'll just
        set all children to have the same size.
        """
        for child in self.children:
            child.setSize(y, x, h, w) 

    def getContents(self):
        """
        call getContents recursively on children, and
        keep the results together in a list which we
        return
        """

        results = []

        for child in self.children:
            results.extend(child.getContents())

        self.log("returning: %s" % results)
        return results
