import re
import htmlentitydefs
from heapq import nlargest
from difflib import SequenceMatcher
from csv import DictReader, Sniffer


UNICHAR_REPLACEMENTS = (
    (u"\xa0",   u" "),      # non breaking space
    (u"\u2013", u"-"),      # en dash
    (u"\u2018", u"`"),      # left single quote
    (u"\u2019", u"'"),      # right single quote
    (u"\u2026", u"..."),    # horizontal ellipsis
    (u"\u201c", u"\""),     # left double quote
    (u"\u201d", u"\""),     # right double quote
)


def is_url(s):
    return s.find("://") > 0


def dict_to_text(d):
    #return "\n".join("{0:s}: {1:s}".format(k, v) for k, v in d.items())
    return u"\n".join(u"{0:s}: {1:s}".format(k, v) for k, v in d.items())


def unescape(text):
    """Removes HTML or XML character references and entities from a text string.

    :param text: The HTML (or XML) source text.

    :returns:   The plain text, as a Unicode string, if necessary.
    """

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def unichar_to_text(text):
    """Convert some common unicode characters to their plain text equivilent.

    This includes for example left and right double quotes, left and right single quotes, etc.
    """

    for replacement in UNICHAR_REPLACEMENTS:
        text = text.replace(*replacement)

    return text


def csv_to_dictlist(csvfile):
    with open(csvfile, "rb") as f:
        dialect = Sniffer().sniff(f.read(1024))
        f.seek(0)
        return list(dict((k.strip(), v.strip()) for k, v in d.items()) for d in DictReader(f, dialect=dialect))


def get_close_matches(word, possibilities, n=3, cutoff=0.6):
    """Use SequenceMatcher to return list of close matches.

    word is a sequence for which close matches are desired (typically a string).

    possibilities is a list of sequences against which to match word (typically a list of strings).

    Optional arg n (default 3) is the maximum number of close matches to return. n must be > 0.

    Optional arg cutoff (default 0.6) is a float in [0.0, 1.0].
    Possibilities that don't score at least that similar to word are ignored.

    The best (no more than n) matches among the possibilities are returned
    in a list, sorted by similarity score, most similar first.

    >>> get_close_matches("appel", ["ape", "apple", "peach", "puppy"])
    ['apple', 'ape']
    >>> import keyword as _keyword
    >>> get_close_matches("wheel", _keyword.kwlist)
    ['while']
    >>> get_close_matches("apple", _keyword.kwlist)
    []
    >>> get_close_matches("accept", _keyword.kwlist)
    ['except']
    """

    if not n > 0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))

    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for x in possibilities:
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and s.quick_ratio() >= cutoff and s.ratio() >= cutoff:
            result.append((x, s.ratio()))

    # Return n largest best scorers and their matches.
    return nlargest(n, result)
