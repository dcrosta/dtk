from core import Drawable

class Select(Drawable):
    """
    Select is a widget which looks like a button when
    unfocused, and shows a horizontal list of choices
    when focused. The list will take up as much room as
    is available to be drawn or as is needed. Selection
    changes with the left and right arrow keys.

    Events:
     * 'selection changed' when the selection changes
     * 'options changed' when the options in the Select
       are changed
    """


    def __init__(self, **kwargs):
        super(Select, self).__init__(**kwargs)

        self.options = []
        self.setValue(None)

        self.bindKey('right', self.nextOption)
        self.bindKey('left', self.prevOption)


    def setOptions(self, options):
        self.options = options
        self.touch()

        self.fireEvent('options changed')


    def setValue(self, value):
        if value in self.options:
            self.value = value
            self.touch()

            self.fireEvent('selection changed')

        elif value is None:
            self.value = ''
            self.touch()

            self.fireEvent('selection changed')


    def getValue(self):
        return self.value

    # alias getValue() as getText() 
    getText = getValue


    def nextOption(self):
        if self.value in self.options:
            index = self.options.index(self.value)
            self.setValue(self.options[(index + 1) % len(self.options)])

        else:
            self.value = self.options[0]

        self.touch()

        self.fireEvent('selection changed')


    def prevOption(self):
        if self.value in self.options:
            index = self.options.index(self.value)
            self.setValue(self.options[(index - 1) % len(self.options)])

        else:
            self.value = self.options[0]

        self.touch()

        self.fireEvent('selection changed')


    def _render(self):
        self.clear()
        
        size = 2 + sum([len(option) for option in self.options]) + len(self.options)

        if self.w >= size and self.focused:
            self.draw('[', 0, 0)
            x = 1
            for option in self.options:
                label = option
                if option == '':
                    label = '<No Value>'
                self.draw(label, 0, x, highlight = (option == self.value))
                x += len(label)
                self.draw(' ', 0, x)
                x += 1

            self.draw(']', 0, x - 1)

        else:
            self.draw(self.value, 0, 0, highlight = self.focused)
