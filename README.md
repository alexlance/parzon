# Parzon - DNS zone file parser

*"Hey, you know how zone files have this god-awful archaic syntax - with lots of
corner cases and syntactical quirks? - well guess which RFCs we need you to brush up on?*"


### Synopsis

Given a dns zone file that is compatible with RFC 1035 (section 5) and RFC 1034 (section 3.6.1), Parzon
attempts to break down the components of the file and provide an interface for querying zone information.


### Features

* Does a reverse dns lookup for CNAMES based on an IP address for input - using only a given zonefile.
  Outputs the CNAMES.

* Monkey patches resource records in zonefiles, so you can see what's going on a little clearer (-d)


### Quick start

> python -m parzon -a <IPADDRESS> path/to/zonefile

And take a quick look at the options:

> python -m parzon --help

Note: if you run *python setup.py install --user* it will build a standalone
parzon binary in ~/.local/bin/.


### More info...

Although it isn't strictly necessary, we're going to assume that each zone file has an $ORIGIN keyword
that tells you what main domain this zonefile relates to.


### Dependencies

* Python 2.7.9 (it may Just Work on other versions too)

