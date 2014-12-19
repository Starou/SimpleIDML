# -*- coding: utf-8 -*-


import re
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from xml.dom.minidom import parseString, Node


# This code came from the Django Project.
# https://github.com/django/django/blob/1.6a1/django/test/testcases.py
class SimpleTestCase(unittest.TestCase):
    def assertXMLEqual(self, xml1, xml2, msg=None):
        """
        Asserts that two XML snippets are semantically the same.
        Whitespace in most cases is ignored, and attribute ordering is not
        significant. The passed-in arguments must be valid XML.
        """
        try:
            result = compare_xml(xml1, xml2)
        except Exception as e:
            standardMsg = 'First or second argument is not valid XML\n%s' % e
            self.fail(self._formatMessage(msg, standardMsg))
        else:
            if not result:
                standardMsg = '%s != %s' % (safe_repr(xml1, True), safe_repr(xml2, True))
                self.fail(self._formatMessage(msg, standardMsg))


# https://github.com/django/django/blob/1.6a1/django/test/utils.py
def compare_xml(want, got):
    """Tries to do a 'xml-comparison' of want and got. Plain string
    comparison doesn't always work because, for example, attribute
    ordering should not be important. Comment nodes are not considered in the
    comparison.

    Based on http://codespeak.net/svn/lxml/trunk/src/lxml/doctestcompare.py
    """
    _norm_whitespace_re = re.compile(r'[ \t\n][ \t\n]+')

    def norm_whitespace(v):
        return _norm_whitespace_re.sub(' ', v)

    def child_text(element):
        return ''.join([c.data for c in element.childNodes
                        if c.nodeType == Node.TEXT_NODE])

    def children(element):
        return [c for c in element.childNodes
                if c.nodeType == Node.ELEMENT_NODE]

    def norm_child_text(element):
        return norm_whitespace(child_text(element))

    def attrs_dict(element):
        return dict(element.attributes.items())

    def check_element(want_element, got_element):
        if want_element.tagName != got_element.tagName:
            return False
        if norm_child_text(want_element) != norm_child_text(got_element):
            return False
        if attrs_dict(want_element) != attrs_dict(got_element):
            return False
        want_children = children(want_element)
        got_children = children(got_element)
        if len(want_children) != len(got_children):
            return False
        for want, got in zip(want_children, got_children):
            if not check_element(want, got):
                return False
        return True

    def first_node(document):
        for node in document.childNodes:
            if node.nodeType != Node.COMMENT_NODE:
                return node

    want, got = strip_quotes(want, got)
    want = want.replace('\\n', '\n')
    got = got.replace('\\n', '\n')

    # If the string is not a complete xml document, we may need to add a
    # root element. This allow us to compare fragments, like "<foo/><bar/>"
    if not want.startswith('<?xml'):
        wrapper = '<root>%s</root>'
        want = wrapper % want
        got = wrapper % got

    # Parse the want and got strings, and compare the parsings.
    want_root = first_node(parseString(want))
    got_root = first_node(parseString(got))

    return check_element(want_root, got_root)


def strip_quotes(want, got):
    """
    Strip quotes of doctests output values:

    >>> strip_quotes("'foo'")
    "foo"
    >>> strip_quotes('"foo"')
    "foo"
    """
    def is_quoted_string(s):
        s = s.strip()
        return (len(s) >= 2
                and s[0] == s[-1]
                and s[0] in ('"', "'"))

    def is_quoted_unicode(s):
        s = s.strip()
        return (len(s) >= 3
                and s[0] == 'u'
                and s[1] == s[-1]
                and s[1] in ('"', "'"))

    if is_quoted_string(want) and is_quoted_string(got):
        want = want.strip()[1:-1]
        got = got.strip()[1:-1]
    elif is_quoted_unicode(want) and is_quoted_unicode(got):
        want = want.strip()[2:-1]
        got = got.strip()[2:-1]
    return want, got


# https://github.com/django/django/blob/1.6a1/django/utils/unittest/util.py
_MAX_LENGTH = 80


def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _MAX_LENGTH:
        return result
    return result[:_MAX_LENGTH] + ' [truncated]...'
