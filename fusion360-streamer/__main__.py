from .application import Application
from .constants import FUSION360_APPID, WINDOWS_OSID, OSX_OSID
from pprint import pprint
from humanize import naturaldate

import argparse
import sys


parser = argparse.ArgumentParser(description="Autodesk Streamer python implementation")
parser.add_argument("-i", "--info", action="store_true", help="Print application information")
parser.add_argument("--packages-info", action="store_true", help="Print the packages info")
parser.add_argument("--sub-applications-info", action="store_true", help="Print the sub applications info")
parser.add_argument("--app-id", type=str, default=FUSION360_APPID, help="The app id")
parser.add_argument("-v", "--versions", action="store_true", help="Get version history of the app using the Wayback Machine API")
parser.add_argument("-p", "--platform", type=str, choices=["windows", "win", "osx", "mac"], default="windows", help="The platform id")
parser.add_argument("-r", "--recurse", action="store_true", help="Recurse into sub applications")
parser.add_argument("-o", "--output-dir", type=str, default="data", help="The output directory")
parser.add_argument("-d", "--download", action="store_true", help="Download the packages to <output-dir>/extracted")
parser.add_argument("-e", "--extract", action="store_true", help="Extract the packages after download to <output-dir>/extracted")
args = parser.parse_args()

if args.platform == "windows" or args.platform == "win":
	platform_id = WINDOWS_OSID
elif args.platform == "osx" or args.platform == "mac":
	platform_id = OSX_OSID
else:
	print("Unknown platform", args.platform)
	exit(1)

app = Application(app_id=args.app_id, os_id=platform_id)
if args.info:
	print(app)
elif args.versions:
	for v in app.snapshot_versions:
		print(naturaldate(v[0]), ":", v[1])
elif args.packages_info:
	pprint(app.packages_info)
elif args.sub_applications_info:
	pprint(app.sub_applications_info)
elif args.download or args.extract:
	app.download(output_dir=args.output_dir, recurse=args.recurse)

	if args.extract:
		app.extract(output_dir=args.output_dir, recurse=args.recurse)
else:
	from .gui import Gui
	from PyQt5.QtWidgets import QApplication

	print("Starting GUI")
	app = QApplication(sys.argv)
	window = Gui()
	window.show()
	sys.exit(app.exec_())
