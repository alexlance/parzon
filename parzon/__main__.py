""" parzone, dns zone file parsing """

import argparse
import sys
import os

def get_options():
    """ Setup the command line arguments. """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('DIR', type=str, nargs='?', default=".",
                        help='')
    parser.add_argument('-f', dest='ipaddr', action='append', required=True,
                        help='Server to be provisioned (flag can be used multiple times)')
    parser.add_argument('-u', dest='username', required=True,
                        help='ssh login username')
    return parser.parse_args()


def check_config(p, path, options):
    """ """
    pass


def main():
    """ """
    options = get_options()
    #p = Message(options.quiet)
    #check_config(p, options.DIR, options)


if __name__ == "__main__":
    main()
