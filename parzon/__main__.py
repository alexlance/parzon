""" parzon, dns zone file parsing """

import argparse
from parzon.zonefile import ZoneFile


def get_options():
    """ Setup the command line arguments. """
    parser = argparse.ArgumentParser(prog='parzon',
                        description='Given an IP address and a DNS zonefile, \
                                     perform reverse DNS search on the file')
    parser.add_argument('ZONEFILE', type=str,
                        help='The path to the zonefile that you want to parse')
    parser.add_argument('-a', dest='address', type=str, required=True,
                        help='An IP address which to do reverse lookups on')
    parser.add_argument('-d', dest='debug', action='store_true',
                        help='Display the monkey-patched version of the zonefile')
    return parser.parse_args()


def main():
    """ Do a reverse dns lookup using only a zonefile. """
    options = get_options()
    z = ZoneFile(options.ZONEFILE, options.debug)
    z.parse()
    results = z.get_cnames_from_ip(options.address)
    for i in results:
        print i


if __name__ == "__main__":
    main()
