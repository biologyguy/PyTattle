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
import signal
from time import time
import datetime
from ftplib import FTP, all_errors
from hashlib import md5
from urllib import request
from urllib.error import URLError, HTTPError, ContentTooShortError
import json
import traceback
from tempfile import TemporaryFile


def ask(input_prompt, default="yes", timeout=0):
    if default == "yes":
        yes_list = ["yes", "y", '']
        no_list = ["no", "n", "abort"]
    else:
        yes_list = ["yes", "y"]
        no_list = ["no", "n", "abort", '']

    def kill(*args):
        raise TimeoutError(args)

    try:
        if os.name == "nt":
            import msvcrt
            timeout = timeout if timeout > 0 else 3600
            start_time = time()
            sys.stdout.write(input_prompt)
            sys.stdout.flush()
            _response = ''
            while True:
                if msvcrt.kbhit():
                    _chr = msvcrt.getche()
                    if ord(_chr) == 13:  # enter_key
                        break
                    elif ord(_chr) >= 32:  # space_char
                        _response += _chr.decode()
                if len(_response) == 0 and (time() - start_time) > timeout:
                    _response = default
                    break

            print('')  # needed to move to next line
            if _response.lower() in yes_list:
                return True
            else:
                return False

        else:
            signal.signal(signal.SIGALRM, kill)
            signal.alarm(timeout)
            _response = input(input_prompt)
            signal.alarm(0)
            while True:
                if _response.lower() in yes_list:
                    return True
                elif _response.lower() in no_list:
                    return False
                else:
                    print("Response not understood. Valid options are 'yes' and 'no'.")
                    signal.alarm(timeout)
                    _response = input(input_prompt)
                    signal.alarm(0)

    except TimeoutError:
        return False


class PyTattle(object):
    """Catch all errors and prepare/send them somewhere"""
    def __init__(self, redirect="email", traceback_type="cleaned", sysinfo="full", prev_error_url=None, **kwargs):
        """

        :param redirect: ["email", "ftp", "github"]
        :param traceback_type: ["full", "cleaned"]
        :param sysinfo: ["full", "none"]
        :param kwargs: email, ftploc, ftplogin, ftppswd, githubloc
        """
        assert redirect in ["email", "ftp", "github"]
        self.redirect = redirect

        assert traceback_type in ["full", "cleaned"]
        self.traceback_type = traceback_type

        assert sysinfo in ["full", "none"]
        self.sysinfo = sysinfo

        self.email = None if "email" not in kwargs else kwargs["email"]

        self.ftploc = None if "ftploc" not in kwargs else kwargs["ftploc"]
        self.ftplogin = None if "ftplogin" not in kwargs else kwargs["ftplogin"]
        self.ftppswd = None if "ftppswd" not in kwargs else kwargs["ftppswd"]

        self.githubloc = None if "githubloc" not in kwargs else kwargs["githubloc"]

        self.prev_error_url = prev_error_url
        return

    def tattle(self, main, *args, **kwargs):
        try:
            print(args)
            print(kwargs)
            main(*args, **kwargs)
        except:
            err = sys.exc_info()
            if self.redirect == "ftp":
                self._send_ftp_traceback(err)
            sys.exit()

    def _error_report(self, trace_back):
        message = ""
        if self.prev_error_url:
            message += self._check_previous_errors()

        permission = ask("%s\nAn error report with the above traceback has been prepared and is ready to send to the "
                         "package developers.\nWould you like to upload the report? [y]/n " % message, timeout=15)
        try:
            if permission:
                print("\nPreparing error report for FTP upload...")
                temp_file = TemporaryFile()
                temp_file.write(trace_back.encode())
                print("Connecting to FTP server...", self.ftploc, self.ftplogin, self.ftppswd)
                ftp = FTP(self.ftploc, user=self.ftplogin, passwd=self.ftppswd, timeout=5)
                # ftp = FTP("rf-cloning.org", user="buddysuite", passwd="seqbuddy", timeout=5)
                print("Sending...")
                ftp.storlines("STOR error_%s" % temp_file.name, temp_file)  # Upload error to FTP
                print("Success! Thank you.")
        except all_errors as e:
                print("Well... We tried. Seems there was a problem with the FTP upload\n%s" % e)
        return

    def _check_previous_errors(self):
        message = ""
        error_hash = re.sub("^#.*?\n{2}", "", trace_back, flags=re.DOTALL)  # Remove error header information before hashing
        error_hash = md5(error_hash.encode("utf-8")).hexdigest()  # Hash the error
        try:  # Check online to see if error has been reported before
            raw_error_data = request.urlopen(self.prev_error_url, timeout=2)
            error_string = raw_error_data.read().decode("utf-8")  # Read downloaded file
            error_string = re.sub("#.*\n", "", error_string)
            error_json = json.loads(error_string)  # Convert JSON into a data table

            version_str = re.search("# [A-Z]?[a-z]+Buddy: (.*)", trace_back).group(1)

            if error_hash in error_json.keys():  # Check if error is known (if it's in the data table)
                if error_json[error_hash][1] == "None" or error_json[error_hash][1] == version_str:  # If error not resolved
                    message += "This is a known bug since version %s, " \
                               "but it has not been resolved yet.\n" % error_json[error_hash][0]

                else:  # If error has been resolved
                    message += "This bug was resolved in version %s. " \
                               "We recommend you upgrade to the latest version.\n" % error_json[error_hash][1]

            else:  # If error is unknown
                message += "Uh oh, you've found a new bug! This issue is not currently in bug tracker.\n"

        except (URLError, HTTPError, ContentTooShortError) as err:  # If there is an error, just blow through
            message += "Failed to locate known error codes:\n%s\n" % str(err)
        return message

    def _send_ftp_traceback(self, e):
        now = datetime.datetime.now()
        tb = ""
        for _line in traceback.format_tb(sys.exc_info()[2]):
            if os.name == "nt":
                _line = re.sub('"(?:[A-Za-z]:)*\{0}.*\{0}(.*)?"'.format(os.sep), r'"\1"', _line)
            else:
                _line = re.sub('"{0}.*{0}(.*)?"'.format(os.sep), r'"\1"', _line)
            tb += _line
        platform = "# Platform: %s\n" % sys.platform
        python = "# Python: %s\n" % re.sub("[\n\r]", "", sys.version)
        date = "# Date: %s\n\n" % now.strftime('%Y-%m-%d')
        error = "%s: %s\n\n" % (type(e).__name__, e)

        tb = "".join([python, platform, date, error, tb])
        print("\033[mYour program has crashed with the following traceback:\033[91m\n\n%s\n\n\033[m" % tb)
        self._error_report(tb)
        return


def main_function(arg1, arg2, doing="something not that important!"):
    print("%s %s Doing %s" % (arg1, arg2, doing))
    # Crash!
    x = 1/0
    return x

if __name__ == '__main__':
    reporter = PyTattle(redirect="ftp", ftploc="rf-cloning.org", ftplogin="buddysuite", ftppswd="seqbuddy")
    reporter.tattle(main_function, 1, 2, doing="Blahh")
