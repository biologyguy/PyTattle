from github3 import GitHub, login
from getpass import getuser
from . import Reporter

# https://gist.github.com/JeffPaine/3145490
# https://github3py.readthedocs.io

class GithubReporter(Reporter):
    required = dict(
        password = (True, str))
    
    def configure(self, user):
        super.configure(user)
        cache = user.get_cache('github')
        if 'api' not in cache:
            cache['api'] = login(
                user.get('github', 'username', getuser()),
                user.get('github', 'password'))
    
    def check_previous(self, error, user=None):
        """Check whether the error was previously reported. Rather than try to
        do fuzzy matching, we simply check whether there is a PyTattle section
        of the first message of the issue, and if so, compare the fingerprint
        against that of the error.
        """
        api = None
        if user is not None:
            cache = user.get_cache('github')
            if 'api' in cache:
                api = cache['api']
        
        if api is None:
            api = GitHub()
        
        