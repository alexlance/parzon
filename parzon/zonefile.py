""" Module to group DNS Zone File related operations. """
import sys
import re


class ZoneFile(object):
    """ Model a DNS Zonefile and provide mechanisms to patch it up into something usable. """
    origin = ''
    ttl = 0
    records = []
    debug = False

    def __init__(self, path, debug=False):
        """ Parse the zonefile into a more usable format.

        Strip comments out. Render multi-lined parenthetical expressions on a single
        line. Replace @ with $ORIGIN. Resource records that begin with a blank, are
        meant to be related to the same resource that exists on the previous line, so
        we'll fill in the blanks too.
        """
        self.debug = debug
        text = self.open_zonefile(path)
        text = self.remove_comments(text)
        self.origin = self.get_origin(text)
        self.ttl = self.get_ttl(text)
        text = self.replace_at_with_origin(text)
        text = self.condense_parenthesis(text)
        self.records = self.get_resource_records(text)

    def open_zonefile(self, path):
        """ Open a dns bind zonefile up, return it as a string. """
        try:
            return open(path).read()
        except Exception, e:
            print "Can't open file at {}: {}".format(path, e)
            sys.exit(1)

    def remove_comments(self, text):
        """ Remove all comments from the zonefile, comments start with a semi-colon. """
        return re.sub(r';.*$', '', text, flags=re.MULTILINE)

    def replace_at_with_origin(self, text):
        """ Replace all instances of the @ symbol at the start of line, with the $ORIGIN. """
        if not self.origin:
            print "Origin hasn't been set, halting."
            sys.exit(1)
        return re.sub(r'^@\s+', self.origin+' ', text, flags=re.MULTILINE)

    def condense_parenthesis(self, text):
        """ Each line represents a single Resource Record, unless that line
        contains a parenthesis. Remove all newline chars from within multiple
        line spanning parentheses.
        """
        condense_brackets = re.compile(r'\((.*?)\)', re.DOTALL)
        return condense_brackets.sub(self.regex_helper_remove_newlines, text)

    def get_origin(self, text):
        """ Most zone files have a keyword called $ORIGIN which specifies the main
        domain name that this zone file represents. A line starting with an @
        symbol represents the value of this $ORIGIN.
        """
        m = re.search(r'\$ORIGIN\s+([\w\.]+)', text)
        if not m:
            print "Can't find $ORIGIN keyword, halting."
            sys.exit(1)
        return m.group(1)

    def get_ttl(self, text):
        """ Get the $TTL directive keyword which specifies the default DNS cache. """
        m = re.search(r'\$TTL\s+([\w\d]+)', text)
        if m:
            return m.group(1)

    def regex_helper_remove_newlines(self, match):
        """ Remove newlines, from within a regex match. """
        return match.group().replace('\n', '')

    def get_resource_records(self, text):
        """ This method monkey-patches the resource records in the zonefile, so
        that each RR has the five fields: name, ttl, class, type, data.
        """
        records = []
        current_name = ''
        for line in text.split("\n"):

            # remove trailing space
            line = line.rstrip()

            # skip past the directives
            if any(word in line for word in ['$ORIGIN ', '$TTL ', '$INCLUDE ', '$GENERATE ']):
                continue

            # skip past blank lines
            if not re.search(r'\w+', line):
                continue

            # if line starts with a space, and has other things on the line, then inherit previous name
            fields = re.split(r'\s+', line)
            if line[0] in [' ', r'\t'] and re.search(r'\w+', line[1:]) and len(current_name):
                fields[0] = current_name
            else:
                current_name = fields[0]

            # insert default ttl
            try:
                if not fields[1][0].isdigit():
                    fields.insert(1, self.ttl)
            except IndexError:
                fields.insert(1, self.ttl)

            # insert the protocol family IN if it's missing
            if len(fields) > 2 and fields[2] not in ['IN', 'HS', 'CH']:
                fields.insert(2, 'IN')

            if len(fields) < 5:
                print "Could not parse this resource record: {}".format(fields)
                sys.exit(1)

            f = {}
            f["name"] = fields[0]
            f["ttl"] = fields[1]
            f["class"] = fields[2]
            f["type"] = fields[3]
            f["data"] = " ".join(fields[4:])
            records.append(f)
            if self.debug:
                print fields
        return records

    def search_via_field(self, field, search):
        """ Search for all resource records, using the last field as the search string,
        eg, for A records it'll be the IP address. Return a list of the matches (well, the
        index to the match, anyway).
        """
        shortlist = []
        for k, v in enumerate(self.records):
            if search == v[field]:
                shortlist.append(k)
        return shortlist
