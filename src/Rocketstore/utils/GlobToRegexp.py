"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
glob-to-reg.py (c) 2023 
Created:  2023-12-01 18:05:15 
Desc: description
Docs: documentation
"""

import re


class GlobToRegexp:

    def __init__(self, glob: str, **kwargs: any):
        if not isinstance(glob, str):
            raise TypeError('Expected a string')

        # The regexp we are building, as a string.
        re_str = ""

        # Whether we are matching so-called "extended" globs (like bash) and should
        # support single character matching, matching ranges of characters, group
        # matching, etc.
        extended = kwargs.get('extended', False)

        # When globstar is _false_ (default), '/foo/*' is translated a regexp like
        # '^\/foo\/.*$' which will match any string beginning with '/foo/'
        # When globstar is _true_, '/foo/*' is translated to regexp like
        # '^\/foo\/[^/]*$' which will match any string beginning with '/foo/' BUT
        # which does not have a '/' to the right of it.
        # E.g. with '/foo/*' these will match: '/foo/bar', '/foo/bar.txt' but
        # these will not '/foo/bar/baz', '/foo/bar/baz.txt'
        # Lastly, when globstar is _true_, '/foo/**' is equivalent to '/foo/*' when
        # globstar is _false_
        globstar = kwargs.get('globstar', False)

        # If we are doing extended matching, this boolean is true when we are inside
        # a group (e.g., {*.html,*.js}), and false otherwise.
        in_group = False

        # RegExp flags (e.g., "i") to pass in to re.compile.
        flags = kwargs.get('flags', "")

        typeFlags = {
            "a": re.A,
            "ascii": re.ASCII,
            "debug": re.DEBUG,
            "i": re.I,
            "ignorecase": re.IGNORECASE,
            "l": re.L,
            "locale": re.LOCALE,
            "g": re.DOTALL,
            "m": re.M,
            "multiline": re.MULTILINE,
            "s": re.S,
            "dotall": re.DOTALL,
            "u": re.U,
            "unicode": re.UNICODE,
            "x": re.X,
            "verbose": re.VERBOSE,
        }

        # Ensure that the specified flags are valid
        flags = typeFlags.get(flags, 0)

        i = 0
        for c in glob:
            if c in ["/", "$", "^", "+", ".", "(", ")", "=", "!", "|"]:
                re_str += "\\" + c

            elif c == "?":
                if extended:
                    re_str += "."

            elif c in ["[", "]"]:
                if extended:
                    re_str += c

            elif c == "{":
                if extended:
                    in_group = True
                    re_str += "("

            elif c == "}":
                if extended:
                    in_group = False
                    re_str += ")"

            elif c == ",":
                if in_group:
                    re_str += "|"
                else:
                    re_str += "\\" + c

            elif c == "*":
                # Move over all consecutive "*"'s.
                # Also store the previous and next characters
                prev_char = glob[:i-1]
                star_count = 1

                while i + 1 < len(glob) and glob[i+1] == "*":
                    star_count += 1
                    i += 1

                next_char = glob[i+1] if i + 1 < len(glob) else None

                if not globstar:
                    # globstar is disabled, so treat any number of "*" as one
                    re_str += ".*"

                else:
                    # globstar is enabled, so determine if this is a globstar segment
                    is_globstar = star_count > 1 and (
                        prev_char == "/" or prev_char is None) and (
                        next_char == "/" or next_char is None)

                    if is_globstar:
                        # it's a globstar, so match zero or more path segments
                        re_str += "((?:[^/]*(?:\/|$))*)"
                        # re_str += "(.*\/)?"
                        i += 1  # move over the "/"
                    else:
                        # it's not a globstar, so only match one path segment
                        re_str += "([^/]*)"
            else:

                re_str += c

            i += 1

        # When regexp 'g' flag is specified don't
        # constrain the regular expression with ^ & $
        if not flags or flags != re.DOTALL:
            re_str = "^" + re_str + "$"

        # Store the compiled regex as an instance variable
        print("\n -> ", re_str, flags)
        self.pattern = re.compile(re_str, flags)

    def match(self, str: str) -> bool:
        print("\npattern: ", self.pattern,  "\nstr: ", str)
        op = self.pattern.search(str)
        print("res: ", op,  "\n----\n")

        return op is not None
