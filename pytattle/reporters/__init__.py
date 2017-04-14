class Reporter(object):
    """Base class for crash reporters.

    Args:
        config: A :class:`Config` object. The options specific to this reporter
            are extracted and stored in :attr:`self.config`.
        kwargs: Any additional config options passed at runtime. These override
            any values in `config`.
    """
    name = 'undefined'
    defaults = {}
    required = {}

    def __init__(self, config, **kwargs):
        self.config = self.defaults.copy()
        if config.has_section(self.name):
            for option in config.options(self.name):
                self.config[option] = config.get(self.name, option)
        self.config.update(kwargs)
    
    def __getattr__(self, name):
        """Returns the configured value for the given attribute, or None.
        """
        return self.config.get(name, None)
    
    def configure(self, user):
        """Obtain any necessary configuration parameters from the user.

        Args:
            user: The user to configure.
        """
        if not user.has_section(self.name):
            user.add_section(self.name)
        for option in self.required:
            if not user.has_option(self.name, option):
                if option in self.config:
                    value = self.config[option]
                else:
                    value = self.ask_for(option)
                # type conversion
                value = self.required[option](value)
                user.set(self.name, option, value)
    
    def ask_for(self, option):
        """Ask the user to enter a configuration value.

        Args:
            option: The option name.
            obscure: Whether to obscure the input (e.g. for passwords).
        """
        #ask(
        #    "Please enter a value for reporting method {} option {}".format(
        #        self.name, option), 
        #    obscure=obscure)
        pass

    def check_previous(self, error, user=None):
        """Check whether an error has been reported previously.

        Args:
            error: The error to check.
            user: The user reporting the error, or None to check whether the
                error has been reported by any user.
        
        Returns:
            True if the error has been reported, else False.
        """
        return False
    
    def report(self, error, user):
        """Report the error.

        Args:
            error: The error to report.
            user: The user reporting the error.
        
        Returns:
            A dict containing any results of reporting the error (depending on
            the reporting method).
        """
        raise NotImplementedError()
