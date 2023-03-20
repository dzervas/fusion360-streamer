import tarfile
from prettyformatter import pprint
from humanize import naturalsize

import argparse
import hashlib
import os
import requests

FUSION360_ID = "73e72ada57b7480280f7a6f4a289729f"
WINDOWS_ID = "67316f5e79bc48318aa5f7b6bb58243d"
OSX_ID = "97e6dd95735340d6ad6e222a520454db"


def sha1sum(filename):
	h = hashlib.sha1()
	b = bytearray(128*1024)
	mv = memoryview(b)
	with open(filename, 'rb', buffering=0) as f:
		while n := f.readinto(mv):
			h.update(mv[:n])
	return h.hexdigest()


class Streamer():
	platform_id = WINDOWS_ID
	app_id = FUSION360_ID
	session = None
	full_json = None
	packages_json = []
	sub_applications_streams = []

	def __init__(self, app_id=FUSION360_ID, platform_id=WINDOWS_ID):
		self.app_id = app_id
		self.platform_id = platform_id
		self.session = requests.Session()
		self._get_full()

	def _get_full(self):
		"""Get the streamer url from the server."""
		response = self.session.get(f"https://dl.appstreaming.autodesk.com/production/{self.platform_id}/{self.app_id}/full.json")
		self.full_json = response.json()

	def version_info(self):
		"""Get the current version info from the server."""

		return {
			"display-name": self.full_json["properties"]["display-name"],
			"required-os": self.full_json["properties"]["required-os"]["friendly-version"] if "required-os" in self.full_json["properties"] else None,
			"build-version": self.full_json["build-version"],
			"major-update-version": self.full_json["major-update-version"] if "major-update-version" in self.full_json else None,
			"patches_build_version": self.full_json["patches_build_version"],
			# "sub-applications": self.full_json["properties"]["sub-applications"] if "sub-applications" in self.full_json["properties"] else None,
		}

	def _get_packages(self):
		for p in self.full_json["packages"]:
			print("Downloading package JSON", p['checksum'])
			response = self.session.get(f"https://dl.appstreaming.autodesk.com/production/packages/{p['checksum']}.json")
			self.packages_json.append(response.json())

	def packages_info(self):
		if len(self.packages_json) != len(self.full_json["packages"]):
			self._get_packages()
		files = []
		for p in self.packages_json:
			files.append({
				"source-id": p["properties"]["source-id"] if "source-id" in p["properties"] else "Unknown",
				"size": naturalsize(p["properties"]["size"]) if "size" in p["properties"] else "Unknown",
				"_cfg-src": p["properties"]["_cfg-src"] if "_cfg-src" in p["properties"] else "Unknown",
			})
		return files

	def download(self, output_dir="data", recurse=True):
		"""Download the packages."""
		if len(self.packages_json) != len(self.full_json["packages"]):
			self._get_packages()

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		for p in self.packages_json:
			if "non-patched" not in p:
				continue

			for f in p["non-patched"]:
				file = f + ".tar.xz"

				if os.path.exists(os.path.join(output_dir, file)) and sha1sum(os.path.join(output_dir, file)) == f:
					print("Skipping downloaded and checked package", file)
					continue

				print("Downloading package", file)
				response = self.session.get(f"https://dl.appstreaming.autodesk.com/production/packages/{file}")
				with open(os.path.join(output_dir, file), "wb") as f:
					f.write(response.content)

		if recurse:
			for p in self.sub_applications_streams:
				p.download(recurse)

	def extract(self, output_dir="data", recurse=True):
		"""Extract the packages."""
		if len(self.packages_json) != len(self.full_json["packages"]):
			self._get_packages()

		if not os.path.exists(output_dir):
			os.makedirs(os.path.join(output_dir, "extracted"))

		for p in self.packages_json:
			if "non-patched" not in p:
				continue

			for f in p["non-patched"]:
				file = f + ".tar.xz"

				dest = os.path.join(output_dir, "extracted", p["root"]["destination"])
				if not os.path.exists(dest):
					os.makedirs(dest)

				print("Extracting package", file)
				with tarfile.open(os.path.join(output_dir, file), "r:xz") as tar:
					tar.extractall(dest)

		if recurse:
			for p in self.sub_applications_streams:
				p.extract(recurse)

	def _get_sub_applications(self):
		for p in self.full_json["properties"]["sub-applications"]:
			self.sub_applications_streams.append(Streamer(p, self.platform_id))

	def sub_applications_info(self):
		if len(self.sub_applications_streams) != len(self.full_json["properties"]["sub-applications"]):
			self._get_sub_applications()
		sub_apps = []
		for p in self.sub_applications_streams:
			sub_apps.append(p.version_info())
		return sub_apps


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Autodesk Streamer python implementation")
	parser.add_argument("--version-info", action="store_true", help="Print the version info")
	parser.add_argument("--packages-info", action="store_true", help="Print the packages info")
	parser.add_argument("--sub-applications-info", action="store_true", help="Print the sub applications info")
	parser.add_argument("--app-id", type=str, default=FUSION360_ID, help="The app id")
	parser.add_argument("--platform", type=str, choices=["windows", "win", "osx", "mac"], default="windows", help="The platform id")
	parser.add_argument("-r", "--recurse", action="store_true", help="Recurse into sub applications")
	parser.add_argument("-o", "--output-dir", type=str, default="data", help="The output directory")
	parser.add_argument("-e", "--extract", action="store_true", help="Extract the packages after download to <output-dir>/extracted")
	args = parser.parse_args()

	if args.platform == "windows" or args.platform == "win":
		platform_id = WINDOWS_ID
	elif args.platform == "osx" or args.platform == "mac":
		platform_id = OSX_ID
	else:
		print("Unknown platform", args.platform)
		exit(1)

	streamer = Streamer(app_id=args.app_id, platform_id=args.platform_id)
	if args.version_info:
		pprint(streamer.version_info())
	elif args.packages_info:
		pprint(streamer.packages_info(), shorten=False)
	elif args.sub_applications_info:
		pprint(streamer.sub_applications_info(), shorten=False)
	else:
		streamer.download(output_dir=args.output_dir, recurse=args.recurse)

		if args.extract:
			streamer.extract(output_dir=args.output_dir, recurse=args.recurse)
