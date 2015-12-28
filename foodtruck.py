import sys
import logging
import argparse
from foodtruck.web import app


parser = argparse.ArgumentParser(
        description="FoodTruck command line utility")
parser.add_argument(
        '--debug',
        help="Show debug information",
        action='store_true')
parser.add_argument(
        '--version',
        help="Print version and exit",
        action='store_true')

args = parser.parse_args()
if args.version:
    try:
        from foodtruck.__version__ import version
    except ImportError:
        print("Can't find version information.")
        args.exit(1)
    print("FoodTruck %s" % version)
    args.exit(0)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if args.debug:
    root_logger.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler(sys.stdout)
if args.debug:
    log_handler.setLevel(logging.DEBUG)
else:
    log_handler.setLevel(logging.INFO)
root_logger.addHandler(log_handler)


app.run(debug=args.debug)

