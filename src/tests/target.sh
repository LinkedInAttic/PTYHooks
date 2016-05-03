#!/usr/bin/env bash
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

# Any changes to the logic in this file should also be accompanied by changes
# to test_ptyhooks.py.
set -e -u -o pipefail
declare -r WORDS="falcon vulture mallard"

read -s _this_input_is_ignored

for word in $WORDS; do
    echo "Repeat: $word"

    read -p "echoed> " response
    if [[ "$word" != "$response" ]]; then
        echo "Word mismatch: $word != $response"
        exit 1
    fi

    read -s -p "silent> " response
    if [[ "$word" != "$response" ]]; then
        echo "Word mismatch: $word != $response"
        exit 1
    fi
done

echo "Repeat: <Done!>"
