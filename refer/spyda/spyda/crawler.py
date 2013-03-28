#!/usr/bin/env python

"""Web Crawler Tool"""

import sys
from time import clock, time
from optparse import OptionParser

from . import crawl
from . import __version__

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    parser.add_option(
        "-a", "--allowed_url",
        action="append", default=None, dest="allowed_urls",
        help="Allowed url to traverse (multiple allowed)."
    )

    parser.add_option(
        "-d", "--max_depth",
        action="store", type=int, default=0, dest="max_depth",
        help="Maximum depth to follow (0 for unlimited)"
    )

    parser.add_option(
        "-p", "--pattern",
        action="append", default=None, dest="patterns",
        help="URL pattern to match (multiple allowed)."
    )

    parser.add_option(
        "-v", "--verbose",
        action="store_true", default=False, dest="verbose",
        help="Enable verbose logging"
    )

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


def main():
    opts, args = parse_options()

    url = args[0]

    if opts.verbose:
        print("Crawling {0:s}".format(url))

    stime = time()
    result = crawl(url, **opts.__dict__)

    if result["urls"]:
        if opts.verbose:
            print("URL(s):")
        print("\n".join(result["urls"]))
    else:
        if opts.verbose:
            print("No URL(s) found!")

    if result["errors"]:
        if opts.verbose:
            print >> sys.stderr, "Error(s):"
        print >> sys.stderr, "\n".join(" {0:d} {1:s}".format(*url) for url in result["errors"])

    if opts.verbose:
        cputime = clock()
        duration = time() - stime
        urls = len(result["urls"])
        urls_per_second = int(urls / duration)

        print("{0:d} urls found in {1:0.2f}s ({2:d}/s) using {3:0.2f}s of CPU time.".format(urls, duration, urls_per_second, cputime))

if __name__ == "__main__":
    main()
