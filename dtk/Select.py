from Drawable import Drawable

class Select(Drawable):

    def __init__(self, parent, name):
        super(Select, self).__init__(parent, name)

        self.options = []
        self.setValue(None)

        self.bindKey('right', self.nextOption)
        self.bindKey('left', self.prevOption)


    def setOptions(self, options):
        self.options = options
        self.touch()


    def setValue(self, value):
        if value in self.options:
            self.value = value
            self.touch()

        elif value is None:
            self.value = ''
            self.touch()


    def getValue(self):
        return self.value

    # alias getText() to getValue()
    getText = getValue


    def nextOption(self):
        if self.value in self.options:
            index = self.options.index(self.value)
            self.setValue(self.options[(index + 1) % len(self.options)])
            self.touch()


    def prevOption(self):
        if self.value in self.options:
            index = self.options.index(self.value)
            self.setValue(self.options[(index - 1) % len(self.options)])
            self.touch()


    def render(self):
        self.clear()
        
        size = 2 + sum([len(option) for option in self.options]) + len(self.options)

        if self.w >= size and self.focused:
            self.draw('[', 0, 0)
            x = 1
            for option in self.options:
                self.draw(option, 0, x, highlight = (option == self.value))
                x += len(option)
                self.draw(' ', 0, x)
                x += 1

            self.draw(']', 0, x - 1)

        else:
            self.draw(self.value, 0, 0, highlight = self.focused)
