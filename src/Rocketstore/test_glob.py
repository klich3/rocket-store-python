"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
test_glob.py (c) 2023 
Created:  2023-12-01 18:07:00 
Desc: test glob to regexp
Docs: documentation
"""

from utils.GlobToRegexp import GlobToRegexp


def assert_match(glob, string, **opts):
    regex = GlobToRegexp(glob, **opts)
    assert regex.match(string), f"Failed: {glob}, {string}, {opts}"


def assert_not_match(glob, string, **opts):
    regex = GlobToRegexp(glob, **opts)
    assert regex.match(string) == False, f"Failed: {glob}, {string}, {opts}"


def test(globstar):

    assert_match("*", "foo")
    assert_match("*", "foo", **{"flags": "g"})

    # Match the end
    assert_match("f*", "foo")
    assert_match("f*", "foo", **{"flags": "g"})

    # Match the start
    assert_match("*o", "foo")
    assert_match("*o", "foo", **{"flags": "g"})

    # Match the middle
    assert_match("f*uck", "firetruck")
    assert_match("f*uck", "firetruck", **{"flags": "g"})

    # Don't match without Regexp "g"
    assert_not_match("uc", "firetruck")
    # Match anywhere with RegExp "g"
    assert_match("uc", "firetruck", **{"flags": "g"})

    # Match zero characters
    assert_match("f*uck", "fuck")
    assert_match("f*uck", "fuck", **{"flags": "g"})

    # More complex matches
    assert_match("*.min.js", "http://example.com/jquery.min.js",
                 **{"globstar": globstar})
    assert_match("*.min.*", "http://example.com/jquery.min.js",
                 **{"globstar": globstar})
    assert_match("*/js/*.js", "http://example.com/js/jquery.min.js",
                 **{"globstar": globstar})

    # More complex matches with RegExp "g" flag (complex regression)
    assert_match("*.min.*", "http://example.com/jquery.min.js",
                 **{"flags": "g"})
    assert_match("*.min.js", "http://example.com/jquery.min.js",
                 **{"flags": "g"})
    assert_match("*/js/*.js", "http://example.com/js/jquery.min.js",
                 **{"flags": "g"})

    # Test string  "\\\\/$^+?.()=!|{},[].*"  represents  <glob>\\/$^+?.()=!|{},[].*</glob>
    # The equivalent regex is:  /^\\\/\$\^\+\?\.\(\)\=\!\|\{\}\,\[\]\..*$/
    # Both glob and regex match:  \/$^+?.()=!|{},[].*

    testStr = "\\\\/$^+?.()=!|{},[].*"
    targetStr = "\\/$^+?.()=!|{},[].*"
    assert_match(testStr, targetStr)
    assert_match(testStr, targetStr, **{"flags": "g"})

    # Equivalent matches without/with using RegExp "g"
    assert_not_match(".min.", "http://example.com/jquery.min.js")
    assert_match("*.min.*", "http://example.com/jquery.min.js")
    assert_match(".min.", "http://example.com/jquery.min.js", **{"flags": "g"})

    assert_not_match("http:", "http://example.com/jquery.min.js")
    assert_match("http:*", "http://example.com/jquery.min.js")
    assert_match("http:", "http://example.com/jquery.min.js", **{"flags": "g"})

    assert_not_match("min.js", "http://example.com/jquery.min.js")
    assert_match("*.min.js", "http://example.com/jquery.min.js")
    assert_match("min.js", "http://example.com/jquery.min.js",
                 **{"flags": "g"})

    # Match anywhere (globally) using RegExp "g"
    assert_match("min", "http://example.com/jquery.min.js", **{"flags": "g"})
    assert_match("/js/", "http://example.com/js/jquery.min.js",
                 **{"flags": "g"})

    assert_not_match("/js*jq*.js", "http://example.com/js/jquery.min.js")
    assert_match("/js*jq*.js", "http://example.com/js/jquery.min.js",
                 **{"flags": "g"})

    # "extended" mode

    # ?: Match one character, no more and no less
    assert_match("f?o", "foo", **{"extended": True})

    assert_not_match("f?o", "fooo", **{"extended": True})
    assert_not_match("f?oo", "foo", **{"extended": True})

    # ?: Match one character with RegExp "g"
    assert_match("f?o", "foo", **{"extended": True,
                 "globstar": globstar, "flags": "g"})
    assert_match("f?o", "fooo", **{"extended": True,
                 "globstar": globstar, "flags": "g"})
    assert_match("f?o?", "fooo", **
                 {"extended": True, "globstar": globstar, "flags": "g"})
    assert_not_match("?fo", "fooo", **
                     {"extended": True, "globstar": globstar, "flags": "g"})
    assert_not_match("f?oo", "foo", **
                     {"extended": True, "globstar": globstar, "flags": "g"})
    assert_not_match("foo?", "foo", **
                     {"extended": True, "globstar": globstar, "flags": "g"})

    # []: Match a character range
    assert_match("fo[oz]", "foo", **{"extended": True})
    assert_match("fo[oz]", "foz", **{"extended": True})
    assert_not_match("fo[oz]", "fog", **{"extended": True})

    # []: Match a character range and RegExp "g" (regresion)
    assert_match("fo[oz]", "foo", **
                 {"extended": True, "globstar": globstar, "flags": "g"})
    assert_match("fo[oz]", "foz", **
                 {"extended": True, "globstar": globstar, "flags": "g"})
    assert_not_match("fo[oz]", "fog", **
                     {"extended": True, "globstar": globstar, "flags": "g"})

    # {}: Match a choice of different substrings
    assert_match("foo{bar,baaz}", "foobaaz", **{"extended": True})
    assert_match("foo{bar,baaz}", "foobar", **{"extended": True})
    assert_not_match("foo{bar,baaz}", "foobuzz", **{"extended": True})
    assert_match("foo{bar,b*z}", "foobuzz", **{"extended": True})

    # {}: Match a choice of different substrings and RegExp "g" (regression)
    assert_match(
        "foo{bar,baaz}", "foobaaz", **{"extended": True, "globstar": globstar, "flags": "g"}
    )
    assert_match(
        "foo{bar,baaz}", "foobar", **{"extended": True, "globstar": globstar, "flags": "g"}
    )
    assert_not_match(
        "foo{bar,baaz}", "foobuzz", **{"extended": True, "globstar": globstar, "flags": "g"}
    )
    assert_match(
        "foo{bar,b*z}", "foobuzz", **{"extended": True, "globstar": globstar, "flags": "g"}
    )

    # More complex "extended" matches
    assert_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://foo.baaz.com/jquery.min.js",
        **{"extended": True},
    )
    assert_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.buzz.com/index.html",
        **{"extended": True},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.buzz.com/index.htm",
        **{"extended": True},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.bar.com/index.html",
        **{"extended": True},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://flozz.buzz.com/index.html",
        **{"extended": True},
    )

    # More complex "extended" matches and RegExp "g" (regresion)
    assert_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://foo.baaz.com/jquery.min.js",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.buzz.com/index.html",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.buzz.com/index.htm",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://moz.bar.com/index.html",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_not_match(
        "http://?o[oz].b*z.com/{*.js,*.html}",
        "http://flozz.buzz.com/index.html",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )

    # "globstar"
    assert_match(
        "http://foo.com/**/{*.js,*.html}",
        "http://foo.com/bar/jquery.min.js",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_match(
        "http://foo.com/**/{*.js,*.html}",
        "http://foo.com/bar/baz/jquery.min.js",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )
    assert_match(
        "http://foo.com/**",
        "http://foo.com/bar/baz/jquery.min.js",
        **{"extended": True, "globstar": globstar, "flags": "g"},
    )

    # Remaining special chars should still match themselves
    # Test string  "\\\\/$^+.()=!|,.*"  represents  <glob>\\/$^+.()=!|,.*</glob>
    # The equivalent regex is:  /^\\\/\$\^\+\.\(\)\=\!\|\,\..*$/
    # Both glob and regex match:  \/$^+.()=!|,.*
    testExtStr = "\\\\/$^+.()=!|,.*"
    targetExtStr = "\\/$^+.()=!|,.*"
    assert_match(testExtStr, targetExtStr, **{"extended": True})
    assert_match(
        testExtStr, targetExtStr, **{"extended": True, "globstar": globstar, "flags": "g"}
    )


# regression
#  globstar false
test(False)
# globstar true
test(True)


# "globstar" specific tests
assert_match("/foo/*", "/foo/bar.txt", **{"globstar": True})
assert_match("/foo/**", "/foo/baz.txt", **{"globstar": True})
assert_match("/foo/**", "/foo/bar/baz.txt", **{"globstar": True})
assert_match("/foo/*/*.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_match("/foo/**/*.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_match("/foo/**/*.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_match("/foo/**/bar.txt", "/foo/bar.txt", **{"globstar": True})
assert_match("/foo/**/**/bar.txt", "/foo/bar.txt", **{"globstar": True})
assert_match("/foo/**/*/baz.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_match("/foo/**/*.txt", "/foo/bar.txt", **{"globstar": True})
assert_match("/foo/**/**/*.txt", "/foo/bar.txt", **{"globstar": True})
assert_match("/foo/**/*/*.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_match("**/*.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_match("**/foo.txt", "foo.txt", **{"globstar": True})
assert_match("**/*.txt", "foo.txt", **{"globstar": True})

assert_not_match("/foo/*", "/foo/bar/baz.txt", **{"globstar": True})
assert_not_match("/foo/*.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_not_match("/foo/*/*.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_not_match("/foo/*/bar.txt", "/foo/bar.txt", **{"globstar": True})
assert_not_match("/foo/*/*/baz.txt", "/foo/bar/baz.txt", **{"globstar": True})
assert_not_match("/foo/**.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_not_match("/foo/bar**/*.txt", "/foo/bar/baz/qux.txt",
                 **{"globstar": True})
assert_not_match("/foo/bar**", "/foo/bar/baz.txt", **{"globstar": True})
assert_not_match("**/.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_not_match("*/*.txt", "/foo/bar/baz/qux.txt", **{"globstar": True})
assert_not_match("*/*.txt", "foo.txt", **{"globstar": True})

assert_not_match(
    "http://foo.com/*",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"extended": True, "globstar": True},
)
assert_not_match(
    "http://foo.com/*", "http://foo.com/bar/baz/jquery.min.js", **{"globstar": True}
)

assert_match(
    "http://foo.com/*", "http://foo.com/bar/baz/jquery.min.js", **{"globstar": False}
)
assert_match(
    "http://foo.com/**", "http://foo.com/bar/baz/jquery.min.js", **{"globstar": True}
)

assert_match(
    "http://foo.com/*/*/jquery.min.js",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"globstar": True},
)
assert_match(
    "http://foo.com/**/jquery.min.js",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"globstar": True},
)
assert_match(
    "http://foo.com/*/*/jquery.min.js",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"globstar": False},
)
assert_match(
    "http://foo.com/*/jquery.min.js",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"globstar": False},
)
assert_not_match(
    "http://foo.com/*/jquery.min.js",
    "http://foo.com/bar/baz/jquery.min.js",
    **{"globstar": True},
)

print("All tests passed!")
