# Copyright 2016 LinkedIn Corp. Licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License.
#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import codecs
import curses
import sys
import time

import ptyhooks

PTY_INPUT_HOOKS = list()
PTY_OUTPUT_HOOKS = list()

LAUNCH_TIME = time.localtime()
IS_APRIL_FOOLS_DAY = (LAUNCH_TIME.tm_mon, LAUNCH_TIME.tm_mday) == (4, 1)

# The smcup and rmcup sequences are used to control switching to and from the
# alternate screen.
curses.setupterm()
SMCUP = curses.tigetstr("smcup")
RMCUP = curses.tigetstr("rmcup")


def input_hook(function):
    """
    Decorator used to expose a function as an input hook.
    """
    PTY_INPUT_HOOKS.append(function)
    return function


def output_hook(function):
    """
    Decorator used to expose a function as an output hook.
    """
    PTY_OUTPUT_HOOKS.append(function)
    return function


@output_hook
def alert_on_prompt(data, subprocess_fd, **kwargs):
    """
    Sound a bell whenever a prompt appears. Useful for being alerted when a
    command has finished or requires user input to proceed.
    """
    if data.endswith((b": ", b"$ ", b"# ", b"> ", b"? ")):
        sys.stdout.write("\a")
        sys.stdout.flush()


if SMCUP and RMCUP:
    @output_hook
    def disable_altscreen(data, subprocess_fd, **kwargs):
        """
        Disable alternate screen by stripping smcup and rmcup sequences.
        """
        return data.replace(SMCUP, b"").replace(RMCUP, b"")


if IS_APRIL_FOOLS_DAY:
    @output_hook
    def no_sudo_for_you(data, subprocess_fd, **kwargs):
        """
        Cancel any sudo prompts that appear.
        """
        if data.startswith(b"[sudo] password for"):
            ptyhooks.write(subprocess_fd, b"\r")
            return data + b"No sudo for you!"


    @input_hook
    def rot_13(data, subprocess_fd, **kwargs):
        """
        Shift all input by 13 characters. Also breaks various terminal escape
        sequences as a result.
        """
        # Use latin1 to avoid complications caused by data that contains
        # invalid UTF-8 sequences.
        return codecs.encode(data.decode("latin1"), "rot13").encode("latin1")
