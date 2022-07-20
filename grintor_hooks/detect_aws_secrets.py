# Copied and adapted from <awslabs/git-secrets> (https://github.com/awslabs/git-secrets)
# Specifically: https://github.com/awslabs/git-secrets/blob/1.3.0/git-secrets#L235-L240
#
# Copyright 2010-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Copyright 2022 Chris Wheeler
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
# http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import re, sys

def main():
    aws = "(AWS|aws|Aws)?_?"
    quote = "(\"|')"
    connect = "\s*(:|=>|=)\s*"
    opt_quote = f"{quote}?"
    pattern1 = "(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"
    pattern2 = fr"{opt_quote}{aws}(SECRET|secret|Secret)?_?(ACCESS|access|Access)?_?(KEY|key|Key){opt_quote}{connect}{opt_quote}[A-Za-z0-9\/+=]{{40}}{opt_quote}"
    pattern3 =  fr"{opt_quote}{aws}(ACCOUNT|account|Account)_?(ID|id|Id)?{opt_quote}{connect}{opt_quote}[0-9]{{4}}\-?[0-9]{{4}}\-?[0-9]{{4}}{opt_quote}"
    combined_patterns = f"{pattern1}|{pattern2}|{pattern3}"
    prog = re.compile(combined_patterns)

    matches = []
    for filename in sys.argv[1:]:
        with open(filename, 'r', encoding='utf-8') as f:
            for match in prog.finditer(f.read()):
                matches.append(match.group(0))

    if matches:
        print(f'Found matching strings in {sys.argv[0]}:')
        for match in matches:
            print(match)
        exit(1)

if __name__ == '__main__':
    main()