from getpass import getpass

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
            user: A User object; the user to configure.
        """
        if not user.has_section(self.name):
            user.add_section(self.name)
        for option in self.required:
            if not user.has_option(self.name, option):
                obsecure, opt_type = self.required[option]
                if option in self.config:
                    value = self.config[option]
                else:
                    value = self.ask_for(option)
                # type conversion
                value = opt_type(value)
                user.set(self.name, option, value)
    
    def ask_for(self, option, prompt=None, obsecure=False):
        """Ask the user to enter a configuration value.

        Args:
            option: The option name.
            obscure: Whether to obscure the input (e.g. for passwords).
        """
        if prompt is None:
            prompt = (
                "Please enter a value for reporting method {method} "
                "option {option}: ")
        return ask(prompt, obscure=obscure, method=self.name, option=option)
    
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

def ask(prompt, obscure=False, **kwargs):
    """Ask user for some information via the command line.
    
    Args:
        prompt: The prompt to show. This string can have placeholders.
        obscure: Whether to obscure the input (as with a password).
        kwargs: Keyword args to use when formatting the prompt string.
    
    Returns:
        The input value.
    """
    prompt = message.format(**kwargs)
    if obscure:
        return getpass(prompt)
    elif sys.version_info >= (3, 0):
        return input(prompt)
    else:
        return raw_input(prompt)