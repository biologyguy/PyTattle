
from pytattle.reporters import User, Error

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

class Report(object):
    """Encapsulates an error report.
    """
    def __init__(self, user, error):
        self.user = user
        self.error = error
        self.results = {}
    
    def send(self, reporters):
        """Send the error via one or more reporters.
        """
        sent = 0
        for reporter in reporters:
            if not reporter.check_previous(self.error, user=self.user):
                result = reporter.report(self.error, user=self.user)
                self.results[reporter.name] = result
        return sent
    
    def as_dict(self, paranoid=False):
        """Convert this report to a simple dict for serialization.

        Args:
            paranoid: Whether to exclude any personally identifiable 
                information. Note: sensitive information such as
                passwords will NEVER be included.
        
        Returns:
            A dict with three keys: user, error, and results.
        """
        return dict(
            user=self.user.as_dict(paranoid),
            error=self.error.as_dict(paranoid),
            results=self.results)