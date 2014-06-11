# Copyright (c) 2014, Fusion-io, Inc.
# Developed by Alexander Boyd
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the Fusion-io, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse, subprocess, sys

# The actual binary search implementation
def bisect(base, candidates, function):
    if not candidates:
        if function(base):
            return 0
        else:
            return 1
    else:
        midpoint = len(candidates) / 2
        before, mid, after = candidates[:midpoint], candidates[midpoint:midpoint + 1], candidates[midpoint + 1:]
        if function(base + before + mid):
            return bisect(base, before, function)
        else:
            return 1 + midpoint + bisect(base + before + mid, after, function)


# Iterated binary search: picks out items that are required in order for a
# particular function to succeed
def iterated_bisect(base, candidates, function):
    candidates = candidates
    split = bisect(base, candidates, function)
    while split > 0 and split <= len(candidates):
        base = base + candidates[split - 1:split]
        candidates = candidates[:split - 1] + candidates[split:]
        split = bisect(base, candidates, function)
    if split:
        raise Exception("Couldn't find any combinations that succeeded")
    return base


def main():
    if len(sys.argv) == 1:
        print >>sys.stderr, "Usage: bisector.py <script> [arg1 [...]]"
        sys.exit(1)
    script = sys.argv[1:]
    items = []
    while True:
        try:
            items.append(raw_input())
        except EOFError:
            break
    
    def function(items):
        p = subprocess.Popen(script, stdin=subprocess.PIPE)
        p.communicate(''.join(i + '\n' for i in items))
        return not p.wait()
    
    results = iterated_bisect([], items, function)
    # Items are discovered back to front, so reverse them
    results = list(reversed(results))
    print >>sys.stderr, str(len(results)) + ' required item' + ('' if len(results) == 1 else 's') + ':'
    print >>sys.stderr
    for result in results:
        print result


if __name__ == '__main__':
    main()


