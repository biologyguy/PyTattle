#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on: Mar 27 2017 

"""
DESCRIPTION OF PROGRAM
"""

import sys
import os
import re
import shutil


class Exception(Exception):
    def __init__(self, crashreporter):
        super(Exception, self).__init__(crashreporter=crashreporter)
        # Do some more stuff to handle crashes


class CrashReporter(object):
    """Catch all errors and prepare/send them somewhere"""
    def __init__(self, redirect="email", traceback="full", sysinfo="full", **kwargs):
        """

        :param redirect: ["email", "ftp", "github"]
        :param traceback: ["full", "cleaned"]
        :param sysinfo: ["full", "none"]
        :param kwargs: email, ftploc, githubloc
        """
        assert redirect in ["email", "ftp", "github"]
        self.redirect = redirect

        assert traceback in ["full", "cleaned"]
        self.traceback = traceback

        assert sysinfo in ["full", "none"]
        self.sysinfo = sysinfo

        self.email = None if "email" not in kwargs else kwargs["email"]
        self.ftploc = None if "ftploc" not in kwargs else kwargs["ftploc"]
        self.githubloc = None if "githubloc" not in kwargs else kwargs["githubloc"]

        return

    def error_report(self, trace_back, permission=False):
        message = ""
        error_hash = re.sub("^#.*?\n{2}", "", trace_back, flags=re.DOTALL)  # Remove error header information before hashing
        error_hash = md5(error_hash.encode("utf-8")).hexdigest()  # Hash the error
        try:  # Check online to see if error has been reported before
            raw_error_data = request.urlopen("https://raw.githubusercontent.com/biologyguy/BuddySuite/error_codes/"
                                             "diagnostics/error_codes", timeout=2)
            error_string = raw_error_data.read().decode("utf-8")  # Read downloaded file
            error_string = re.sub("#.*\n", "", error_string)
            error_json = json.loads(error_string)  # Convert JSON into a data table

            version_str = re.search("# [A-Z]?[a-z]+Buddy: (.*)", trace_back).group(1)

            if error_hash in error_json.keys():  # Check if error is known (if it's in the data table)
                if error_json[error_hash][1] == "None" or error_json[error_hash][1] == version_str:  # If error not resolved
                    message += "This is a known bug since version %s, " \
                               "but it has not been resolved yet.\n" % error_json[error_hash][0]

                else:  # If error has been resolved
                    print("This bug was resolved in version %s. We recommend you upgrade to the latest version (if you "
                          "downloaded BuddySuite using pip, use the command pip install "
                          "buddysuite --upgrade).\n" % error_json[error_hash][1])
                    return

            else:  # If error is unknown
                message += "Uh oh, you've found a new bug! This issue is not currently in our bug tracker.\n"

        except (URLError, HTTPError, ContentTooShortError) as err:  # If there is an error, just blow through
            message += "Failed to locate known error codes:\n%s\n" % str(err)

        if permission:
            message += "An error report with the above traceback is being sent to the BuddySuite developers because " \
                       "you have elected to participate in the Software Improvement Program. You may opt-out of this " \
                       "program at any time by re-running the BuddySuite installer.\n"
            print(message)
        else:
            permission = ask("%s\nAn error report with the above traceback has been prepared and is ready to send to the "
                             "BuddySuite developers.\nWould you like to upload the report? [y]/n " % message, timeout=15)
        try:
            if permission:
                print("\nPreparing error report for FTP upload...")
                temp_file = TempFile()
                temp_file.write(trace_back)
                print("Connecting to FTP server...")
                ftp = FTP("rf-cloning.org", user="buddysuite", passwd="seqbuddy", timeout=5)
                print("Sending...")
                ftp.storlines("STOR error_%s" % temp_file.name, open(temp_file.path, "rb"))  # Upload error to FTP
                print("Success! Thank you.")
        except all_errors as e:
                print("Well... We tried. Seems there was a problem with the FTP upload\n%s" % e)
        return

    def send_traceback(self, tool, function, e, version):
        now = datetime.datetime.now()
        config = config_values()
        tb = ""
        for _line in traceback.format_tb(sys.exc_info()[2]):
            if os.name == "nt":
                _line = re.sub('"(?:[A-Za-z]:)*\{0}.*\{0}(.*)?"'.format(os.sep), r'"\1"', _line)
            else:
                _line = re.sub('"{0}.*{0}(.*)?"'.format(os.sep), r'"\1"', _line)
            tb += _line
        bs_version = "# %s: %s\n" % (tool, version.short())
        func = "# Function: %s\n" % function
        platform = "# Platform: %s\n" % sys.platform
        python = "# Python: %s\n" % re.sub("[\n\r]", "", sys.version)
        user = "# User: %s\n" % config['user_hash']
        date = "# Date: %s\n\n" % now.strftime('%Y-%m-%d')
        error = "%s: %s\n\n" % (type(e).__name__, e)

        tb = "".join([bs_version, func, python, platform, user, date, error, tb])
        print("\033[m%s::%s has crashed with the following traceback:\033[91m\n\n%s\n\n\033[m" % (tool, function, tb))
        error_report(tb, config["diagnostics"])
        return


if __name__ == '__main__':
    reporter = CrashReporter(email="biologyguy@gmail.com")
