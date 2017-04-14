class Reporter(object):
    """Base class for crash reporters.
    """
    name = 'undefined'
    defaults = {}
    
    def __init__(self, **kwargs):
        self.config = self.defaults.copy()
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
