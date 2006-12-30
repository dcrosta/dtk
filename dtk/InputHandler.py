import curses

class InputHandler(object):
    """
    The base class for objects which deal with keyboard and
    pseudo-key input.
    """

    # remap certain printable inputs for output
    printableVersion = {
        'space':' '
        }


    def __init__(self, **kwargs):
        # keybindings dict
        self.keybindings = {}


    def handleInput(self, input):
        """
        first sees if the InputHandler is set up to handle printable
        input by looking for the 'printable' key in self.keybindings.
        if so, then the printable characters method is called with
        optional userdata. if not, processing proceeds as below:

        if we can find key in self.keybindings, then we execute the
        associated function with the associated userdata and return
        the result of the method (True or False) to indicate that
        handling is finished, or else we return False to indicate that
        this InputHandler's parent should be asked to handle the
        input
        """

        self.log.debug("handleInput('%s')", input)

        method = None
        args   = []
        kwargs = {}
                
        if 'printable' in self.keybindings and self.isprintable(input):
            (method, args, kwargs) = self.keybindings['printable']

            if len(input) > 1:
                input = self.printableVersion[input] # map things like 'space' => ' '

            # if the method is asking for a _input_key argument,
            # supply it to the method before calling it
            # unless another input key is already being supplied to the method
            # TODO this is actually broken (see below)
            if '_input_key' in method.func_code.co_varnames:
                #kwargs['_input_key'] = kwargs.get('_input_key', None) or input
                kwargs['_input_key'] = input

        elif input in self.keybindings:
            (method, args, kwargs) = self.keybindings[input]

        else:
            return False
        
        # if the method is asking for a _source_obj argument,
        # bind the present object to the method before calling it
        # unless another object is already bound to the method
        # TODO this is actually broken. it will still fill the slot
        # if the user passes in a POSITIONAL argument for _source_obj,
        # resulting in an exception.
        if '_source_obj' in method.func_code.co_varnames:
            kwargs['_source_obj'] = kwargs.get('_source_obj', None) or self

        ret = method(*args, **kwargs)
        return True


    def bindKey(self, key, method, *args, **kwargs):
        """
        tell the input subsystem that the given key should
        have the effect of calling the given method with
        the given arguments and keyword arguments
        """
        self.keybindings[key] = (method, args, kwargs)


    def unbindKey(self, key):
        """
        removes the binding for key from the InputHandler's
        keybindings, if it exists. removing the pseudo-key 'all'
        removes all keybindings from the InputHandler.
        """

        if key == 'all':
            for key in self.keybindings.keys():
                del(self.keybindings[key])

        elif key in self.keybindings:
            del(self.keybindings[key])


    def bindPrintable(self, method, *args, **kwargs):
        """
        tell the input subsystem that printable characters
        should be passed to the given method as they arrive.
        printable characters are anything for which
        curses.ascii.isprint() returns True. 
        """
        self.keybindings['printable'] = (method, args, kwargs)


    def unbindPrintable(self):
        """
        tells the input subsystem that we don't want to handle
        printable character input
        """
        self.unbindKey('printable')


    def isprintable(self, input):
        if input in self.printableVersion:
            return True
        elif len(input) > 1:
            return False
        else:
            return curses.ascii.isprint(input)

