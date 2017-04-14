"""
"""
import base64
from configparser import ConfigParser
import io
import logging
import os

class TattleError(Exception):
    """Base exception class for PyTattle.
    """
    pass

class Config(ConfigParser):
    """Subclass of ConfigParser that adds read_encrypted and write_encrypted
    methods.
    """
    def __init__(self, config_file, passphrase=None, salt=None):
        # Not great to store this in memory, but otherwise we have to
        # constantly ask the user for it.
        super().__init__()
        self.config_file = config_file
        self.passphrase = passphrase
        if passphrase:
            self.crypter = Crypter(salt)
        if os.path.exists(config_file):
            self.read()
    
    def read(self):
        """Load config from an encrypted file.

        Args:
            path: Path to the config file.
            passphrase: The passphrase for encryption.
        """
        if self.passphrase:
            with open(self.config_file, 'rb') as inp:
                decrypted = self.crypter.decrypt(inp.read(), self.passphrase)
                self.read_string(decrypted)
        else:
            super().read(self.config_file)
    
    def write(self):
        """Encrypt the config and write to a file.

        Args:
            path: Path to the config file.
            passphrase: The passphrase for encryption.
        """
        if self.passphrase:
            string = io.StringIO()
            super().write(string)
            encrypted = self.crypter.decrypt(string.getvalue(), self.passphrase)
            with open(self.config_file, 'wb') as out:
                out.write(encrypted)
        else:
            super().write(self.config_file)

class Crypter(object):
    """Wrapper around cryptography that imports necessarily libraries
    when instantiated, and performs encryption/decryption using the
    Fernet recipe with a user-provided password and a random salt.

    Args:
        salt: A salt to use for encryption/decryption. Can be either a path
            to a file where to read the salt or store a new salt, or bytes.
    """
    def __init__(self, salt=None):
        try:
            import cryptography.fernet
            import cryptography.hazmat.backends
            import cryptography.hazmat.primitives.hashes
            import cryptography.hazmat.primitives.kdf.pbkdf2
            self._cryptography_modules = (
                cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC,
                cryptography.hazmat.primitives.hashes.SHA256,
                cryptography.hazmat.backends.default_backend,
                cryptography.fernet.Fernet)
        except ImportError as imperr:
            raise TattleError(
                "There was an error importing the cryptography library, "
                "which is required for file encryption") from imperr
        
        if isinstance(salt, str):
            if os.path.exists(salt):
                with open(salt, 'rb') as inp:
                    salt = inp.read()
        else:
            salt = os.urandom(16)
            with open(salt, 'wb') as out:
                out.write(salt)
        self.salt = salt
    
    def encrypt(self, content, passphrase):
        """Encrypt `content` with a key derived from `phassphrase`.

        Args:
            content: Content to encrypt (string).
            passphrase: The user-supplied phassphrase.
        
        Returns:
            Encrypted content (bytes).
        """
        fernet = self._get_fernet(passphrase, self.salt)
        return fernet.encrypt(content.encode())
    
    def decrypt(self, content, passphrase):
        """Decrypt `content` with a key derived from `passphrase`.

        Args:
            content: Content to decrypt (bytes).
            passphrase: The user-supplied passphrase.
        
        Returns:
            Decrypted content (string).
        """
        fernet = self._get_fernet(passphrase, self.salt)
        return fernet.decrypt(content).decode()
    
    def _get_fernet(self, passphrase, salt):
        """Create a :class:`crypography.fernet.Fernet` instance.

        Args:
            passphrase: The user-supplied phassphrase.
            salt: The random salt.
        """
        kdf = self._cryptography_modules[0](
            algorithm=self._cryptography_modules[1],
            length=32,
            salt=salt,
            iterations=100000,
            backend=self._cryptography_modules[2]())
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return self._cryptography_modules[3](key)

class User(Config):
    """Information about the user, including any necessary credentials.
    """
    def __init__(self, config_file='.tattle', passphrase=None, salt=None):
        super().__init__(config_file, passphrase, salt)
    
    def set_section(self, section_name, options):
        """Add a section to the config file. If the section already exists,
        values are overwritten.
        """
        if not self.has_section(section_name):
            self.add_section(section_name)
        for option, value in options.items():
            self.set(section_name, option, value)
    
    def as_dict(self, paranoid=False):
        """Convert this user to a simple dict for serialization.

        Args:
            paranoid: Whether to exclude any personally identifiable 
                information. Note: sensitive information such as
                passwords will NEVER be included.
        """
        pass

class ErrorFactory(object):
    """Stores application metadata that should be sent with every error, and
    creates new :class:`Error` instances from exceptions.
    """
    def __init__(self, **application_metadata):
        self.application_metadata = application_metadata
        self.system_metadata = self._get_system_metadata()
    
    def create(self, exc=None, **kwargs):
        """Create a new :class:`Error` from an exception.

        Args:
            exc: The exception, or None to generate the error parameters from
                the current application state.
            kwargs: Additional arguments to pass to the :class:`Error`
                constructor. These will override any derived values.
        """
        pass
    
    def _get_system_metadata(self):
        """Get the system metadata to add to the error.
        """
        pass

class Error(object):
    """Contains all relevant information about an error to be reported.

    Args:
        application_metadata: The application metadata to send.
        system_metadata: The system metadata to send.
        package_name: The package that generated the error.
        module_name: The module that generated the error.
        method_name: The method that generated the error.
        lineno: The line in the module where the error was generated.
        exc_type: The exception class.
        exc_value: The exception instance.
        exc_message: The exception message.
        traceback: The python stacktrace.
    """
    def __init__(
            self, application_metadata, system_metadata, lineno, package_name, 
            module_name, exc_type, exc_value, exc_message, traceback, 
            timestamp):
        pass
    
    def as_dict(self, paranoid=False):
        """Convert this error to a simple dict for serialization.

        Args:
            paranoid: Whether to exclude any personally identifiable 
                information. Note: sensitive information such as
                passwords will NEVER be included.
        """
        pass

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
