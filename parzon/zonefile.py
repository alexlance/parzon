""" Module to group DNS Zone File related operations. """
import sys
import re


class ZoneFile(object):
    """ Model a DNS Zonefile and provide mechanisms to patch it up into something usable. """
    _origin = ''
    _ttl = 0
    _debug = False
    _text = ''
    _records = []
    _FNAME, _FTTL, _FCLASS, _FTYPE, _FDATA = 0, 1, 2, 3, 4

    def __init__(self, path, debug=False):
        """ Try and open up a zonefile and read its contents. """
        self._debug = debug
        self._text = self._open_zonefile(path)

    def parse(self):
        """ Parse the zonefile into a more usable format.

        Strip comments out. Render multi-lined parenthetical expressions on a single
        line. Replace @ with $ORIGIN. Resource records that begin with a blank, are
        meant to be related to the same resource that exists on the previous line, so
        we'll fill in the blanks too.
        """
        if not self._text:
            print "The zone file appears to be empty."
            sys.exit(1)
        text = self._text
        text = self._remove_comments(text)
        self._origin = self._get_origin(text)
        self._ttl = self._get_ttl(text)
        text = self._replace_at_with_origin(text)
        text = self._condense_parenthesis(text)
        self._records = self._parse_resource_records(text)

    def get_cnames_from_ip(self, address):
        """ Do some passes across the zonefile, to return all the cnames related to a particular
        IP address. """
        if not len(self._records):
            self.parse()

        results = []
        results += self._search_via_field(self._FDATA, address)

        # If found some names, then search again for records using those names
        for k in results:
            results += self._search_via_field(self._FDATA, self._records[k][self._FNAME])
            results += self._search_via_field(self._FDATA, "{}.{}".format(self._records[k][self._FNAME], self._origin))

        # And then search on those results too.
        for k in results:
            results += self._search_via_field(self._FDATA, self._records[k][self._FNAME])

        # uniquify list
        results = list(set(results))

        # return results
        rtn = []
        for i in results:
            if self._records[i][self._FTYPE] == 'CNAME':
                if self._records[i][self._FNAME] != self._origin:
                    rtn.append("{}.{}".format(self._records[i][self._FNAME], self._origin[:-1]))
                else:
                    rtn.append("{}".format(self._origin[:-1]))
        return rtn

    def _search_via_field(self, field, search):
        """ Search for all resource records, using the specified "field" as the search string,
        eg, for A records it'll be the IP address. Return a list of the matches (well, the
        index to the match, anyway).
        """
        if not len(self._records):
            self.parse()
        shortlist = []
        for k, v in enumerate(self._records):
            if search == v[field]:
                shortlist.append(k)
        return shortlist

    def _open_zonefile(self, path):
        """ Open a dns bind zonefile up, return it as a string. """
        try:
            return open(path).read()
        except Exception, e:
            print "Can't open file at {}: {}".format(path, e)
            sys.exit(1)

    def _remove_comments(self, text):
        """ Remove all comments from the zonefile, comments start with a semi-colon. """
        return re.sub(r';.*$', '', text, flags=re.MULTILINE)

    def _replace_at_with_origin(self, text):
        """ Replace all instances of the @ symbol at the start of line, with the $ORIGIN. """
        if not self._origin:
            print "Origin hasn't been set, halting."
            sys.exit(1)
        return re.sub(r'^@\s+', self._origin+' ', text, flags=re.MULTILINE)

    def _condense_parenthesis(self, text):
        """ Each line represents a single Resource Record, unless that line
        contains a parenthesis. Remove all newline chars from within multiple
        line spanning parentheses.
        """
        condense_paren = re.compile(r'\((.*?)\)', re.DOTALL)
        return condense_paren.sub(self._regex_helper_remove_newlines, text)

    def _get_origin(self, text):
        """ Most zone files have a keyword called $ORIGIN which specifies the main
        domain name that this zone file represents. A line starting with an @
        symbol represents the value of this $ORIGIN.
        """
        m = re.search(r'\$ORIGIN\s+([\w\.]+)', text)
        if not m:
            print "Can't find $ORIGIN keyword, halting."
            sys.exit(1)
        return m.group(1)

    def _get_ttl(self, text):
        """ Get the $TTL directive keyword which specifies the default DNS cache. """
        m = re.search(r'\$TTL\s+([\w\d]+)', text)
        if m:
            return m.group(1)

    def _regex_helper_remove_newlines(self, match):
        """ Remove newlines, from within a regex match. """
        return match.group().replace('\n', '')

    def _parse_resource_records(self, text):
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

            # break up the line into a fields list, splitting on whitespace
            fields = re.split(r'\s+', line)

            # if line starts with a space, and has other things on the line, then inherit previous name
            if line[0] in [' ', r'\t'] and re.search(r'\w+', line[1:]) and len(current_name):
                fields[self._FNAME] = current_name
            else:
                current_name = fields[self._FNAME]

            # insert default ttl
            try:
                if not fields[self._FTTL][0].isdigit():
                    fields.insert(self._FTTL, self._ttl)
            except IndexError:
                fields.insert(self._FTTL, self._ttl)

            # insert the protocol family IN if it's missing
            if len(fields) > 2 and fields[self._FCLASS] not in ['IN', 'HS', 'CH']:
                fields.insert(self._FCLASS, 'IN')

            if len(fields) < 5:
                print "Could not parse this resource record: {}".format(fields)
                sys.exit(1)

            records.append(fields)
            if self._debug:
                print fields
        return records
