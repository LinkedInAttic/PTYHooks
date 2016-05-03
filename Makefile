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
BINDIR=$(HOME)/bin

# If Python 2 and Python 3 are available as distinct binaries, the test suite
# will be executed against both of versions of Python. Otherwise, just test the
# script with the default interpreter.
PYTHON2=$(shell which python2 2> /dev/null)
PYTHON3=$(shell which python3 2> /dev/null)
INTERPRETERS=$(if $(and $(PYTHON2),$(PYTHON3)), $(PYTHON2) $(PYTHON3), python)

# This input will be piped into the subprocess as soon as it launched. The test
# will then compare the input it receives to the contents of this environment
# variable.
export EXPECTED_INPUT=input_hook_test

install: $(BINDIR)/ptyhooks

$(BINDIR)/ptyhooks: src/ptyhooks.py
	@if [ -e $@ ] && ! [ -h $@ ]; then \
		echo "Cannot replace existing file $@: not a symlink."; \
		exit 1; \
	fi
	ln -f -s $(PWD)/$^ $@

test:
	@echo "Running tests:"
	@for python in $(INTERPRETERS); do \
		$$python -V; \
		echo ---; \
		printf "$(EXPECTED_INPUT)\r" | $$python ./src/ptyhooks.py \
		  -c src/tests/test-hooks.py ./src/tests/target.sh || fail=1; \
		echo; \
	done; \
	if [ ! -z "$$fail" ]; then \
		exit 1; \
	fi
	@echo "Testing completed successfully."
