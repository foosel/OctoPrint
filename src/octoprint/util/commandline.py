# coding=utf-8
from __future__ import absolute_import

__author__ = "Gina Häußge <osd@foosel.net>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Copyright (C) 2015 The OctoPrint Project - Released under terms of the AGPLv3 License"


import sarge
import logging
import re


# These regexes are based on the colorama package
# Author: Jonathan Hartley
# License: BSD-3 (https://github.com/tartley/colorama/blob/master/LICENSE.txt)
# Website: https://github.com/tartley/colorama/
_ANSI_CSI_PATTERN = "\001?\033\[(\??(?:\d|;)*)([a-zA-Z])\002?"  # Control Sequence Introducer
_ANSI_OSC_PATTERN = "\001?\033\]((?:.|;)*?)(\x07)\002?"         # Operating System Command
_ANSI_REGEX = re.compile("|".join([_ANSI_CSI_PATTERN,
                                   _ANSI_OSC_PATTERN]))


def clean_ansi(line):
    """
    Removes ANSI control codes from ``line``.

    Parameters:
        line (str or unicode): the line to process

    Returns:
        (str or unicode) The line without any ANSI control codes

    Example::

        >>> text = "Some text with some \x1b[31mred words\x1b[39m in it"
        >>> clean_ansi(text)
        'Some text with some red words in it'
        >>> text = "We \x1b[?25lhide the cursor here and then \x1b[?25hshow it again here"
        >>> clean_ansi(text)
        'We hide the cursor here and then show it again here'
    """
    return _ANSI_REGEX.sub("", line)


class CommandlineError(Exception):
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class CommandlineCaller(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self.on_log_call = lambda *args, **kwargs: None
        self.on_log_stdout = lambda *args, **kwargs: None
        self.on_log_stderr = lambda *args, **kwargs: None

    def checked_call(self, command, **kwargs):
        returncode, stdout, stderr = self.call(command, **kwargs)

        if returncode != 0:
            raise CommandlineError(returncode, stdout, stderr)

        return returncode, stdout, stderr

    def call(self, command, **kwargs):
        if isinstance(command, (list, tuple)):
            joined_command = " ".join(command)
        else:
            joined_command = command
        self._logger.debug(u"Calling: {}".format(joined_command))
        self.on_log_call(joined_command)

        kwargs.update(dict(async=True, stdout=sarge.Capture(), stderr=sarge.Capture()))

        p = sarge.run(command, **kwargs)
        p.wait_events()

        all_stdout = []
        all_stderr = []
        try:
            while p.returncode is None:
                lines = p.stderr.readlines(timeout=0.5)
                if lines:
                    lines = self._preprocess_lines(*lines)
                    self._log_stderr(*lines)
                    all_stderr += list(lines)

                lines = p.stdout.readlines(timeout=0.5)
                if lines:
                    lines = self._preprocess_lines(*lines)
                    self._log_stdout(*lines)
                    all_stdout += list(lines)

                p.commands[0].poll()

        finally:
            p.close()

        lines = p.stderr.readlines()
        if lines:
            lines = self._preprocess_lines(*lines)
            self._log_stderr(*lines)
            all_stderr += lines

        lines = p.stdout.readlines()
        if lines:
            lines = self._preprocess_lines(*lines)
            self._log_stdout(*lines)
            all_stdout += lines

        return p.returncode, all_stdout, all_stderr

    def _log_stdout(self, *lines):
        self.on_log_stdout(*lines)

    def _log_stderr(self, *lines):
        self.on_log_stderr(*lines)

    def _preprocess_lines(self, *lines):
        return lines
