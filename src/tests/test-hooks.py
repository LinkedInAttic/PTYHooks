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
"""
PTYHooks module used for testing.

This module is designed to work in concert with ./src/tests/target.sh to test
the ptyhooks module. Any changes to the logic in this file should also be
accompanied by changes to target.sh. If this test hangs, it likely means that
the altered input returned by `initial_input_hook` is never seen by the
subprocess.
"""
import os
import sys

import ptyhooks

PTY_INPUT_HOOKS = list()
PTY_OUTPUT_HOOKS = list()

EXPECTED_INPUT = os.environ["EXPECTED_INPUT"].encode("utf-8")
INPUT_HOOK_FIRED = list()
TEST_STATE = dict()
TRANSFORMED_USER_INPUT = b"Input transformation is working."


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


@input_hook
def initial_input_hook(data, subprocess_fd, **kwargs):
    """
    When the test script is launched, some text should be piped into it
    immediately with no terminating newline. Since target.sh is executed in the
    context of a PTY, this would normally hang. However, this hook adds a
    carriage return to the text that should be forwarded to the subprocess.
    """
    assert not INPUT_HOOK_FIRED, "Input hook fired twice instead of once."
    assert EXPECTED_INPUT == data.strip(), \
           "Expected %r but received %r" % (EXPECTED_INPUT, data)
    INPUT_HOOK_FIRED.append(True)
    TEST_STATE["expectation"] = TRANSFORMED_USER_INPUT
    return TRANSFORMED_USER_INPUT + b"\r"


@output_hook
def output_monitoring_hook(data, subprocess_fd, **kwargs):
    """
    This hook handles data from the tested subprocess, checks to see what text
    it should send to the subprocess and verifies the subprocess's output
    matches what it expects.
    """
    assert INPUT_HOOK_FIRED, "Output hook executed before input hook."

    lines = data.splitlines()
    for line in lines:
        line = line.strip()

        expectation = TEST_STATE.get("expectation")
        if expectation:
            assert line.startswith(expectation), \
                   "Expected %r but saw %r instead." % (expectation, line)
            TEST_STATE["expectation"] = None

        # When a "Repeat:" line is encountered, retrieve the text it expects to
        # be entered.
        if line.startswith(b"Repeat:"):
            _, TEST_STATE["repeat_this"] = line.split()
            TEST_STATE["expectation"] = b"echoed>"

        # When a line begins with "echoed>", the requested text should be
        # entered, and the application should expect to see the text reprinted.
        elif line.startswith(b"echoed>"):
            TEST_STATE["expectation"] = TEST_STATE["repeat_this"]
            ptyhooks.write(subprocess_fd, TEST_STATE["repeat_this"] + b"\r")

        # When a line begins with "echoed>", the requested text should be
        # entered, the next thing that should be expected is "Repeat:" because
        # input is not echoed for "silent>" prompts.
        elif line.startswith(b"silent>"):
            TEST_STATE["expectation"] = b"Repeat:"
            ptyhooks.write(subprocess_fd, TEST_STATE["repeat_this"] + b"\r")
