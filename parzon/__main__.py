""" parzon, dns zone file parsing """

import argparse
from parzon.zonefile import ZoneFile


def get_options():
    """ Setup the command line arguments. """
    parser = argparse.ArgumentParser(prog='parzon', description='Given an IP address and a DNS zonefile, perform reverse DNS search on the file')
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

    # Gather results from zonefile, doing a lookup on the last field
    # of a resource record (the IP address of A records)
    results = []
    results += z.search_via_field('data', options.address)

    # If found some names, then search again for records using those names
    for k in results:
        results += z.search_via_field('data', z.records[k]['name'])
        results += z.search_via_field('data', "{}.{}".format(z.records[k]['name'], z.origin))

    # And then search on those results too. This could have all been made into
    # a recursive search, but I'm playing it safe - going to assume there are
    # zonefiles out there that would have sufficient complexity (or errors) that
    # would make debugging a recursive solution a bit of a nightmare.
    for k in results:
        results += z.search_via_field('data', z.records[k]['name'])

    # uniquify
    results = list(set(results))

    # print results
    for i in results:
        if z.records[i]['type'] == 'CNAME':
            if z.records[i]['name'] != z.origin:
                print "{}.{}".format(z.records[i]['name'], z.origin[:-1])
            else:
                print "{}".format(z.origin[:-1])




if __name__ == "__main__":
    main()

