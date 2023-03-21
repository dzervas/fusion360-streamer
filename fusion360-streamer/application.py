from .constants import FUSION360_APPID, WINDOWS_OSID, OSX_OSID
from .package import Package
from datetime import datetime
from humanize import naturalsize
import requests



class Application():
	os_id = WINDOWS_OSID
	app_id = FUSION360_APPID
	session = None
	full_json = None
	packages = []
	sub_applications = []

	def __init__(self, app_id=FUSION360_APPID, os_id=WINDOWS_OSID, session=requests.Session(), archive_timestamp=None):
		self.app_id = app_id
		self.os_id = os_id
		self.session = session
		self.full_json = self._get_full_json(archive_timestamp)

	def _get_full_json(self, archive_timestamp=None):
		"""Get the streamer url from the server."""

		response = None
		if archive_timestamp is not None:
			response = self.session.get(f"https://web.archive.org/web/{archive_timestamp}/https://dl.appstreaming.autodesk.com/production/{self.os_id}/{self.app_id}/full.json")
		else:
			response = self.session.get(f"https://dl.appstreaming.autodesk.com/production/{self.os_id}/{self.app_id}/full.json")

		return response.json()

	def _get_packages(self):
		for p in self.full_json["packages"]:
			print("Downloading package JSON", p['checksum'])
			response = self.session.get(f"https://dl.appstreaming.autodesk.com/production/packages/{p['checksum']}.json")
			self.packages.append(Package(response.json()))

	def _get_sub_applications(self):
		for p in self.full_json["properties"]["sub-applications"]:
			self.sub_applications.append(Application(p, self.os_id, self.session))

	@property
	def info(self):
		"""Get the current version info from the server."""

		return {
			"display-name": self.full_json["properties"]["display-name"],
			"required-os": self.full_json["properties"]["required-os"]["friendly-version"] if "required-os" in self.full_json["properties"] else None,
			"build-version": self.full_json["build-version"],
			"major-update-version": self.full_json["major-update-version"] if "major-update-version" in self.full_json else None,
			"patches_build_version": self.full_json["patches_build_version"],
			"sub-applications": self.full_json["properties"]["sub-applications"] if "sub-applications" in self.full_json["properties"] else None,
		}

	@property
	def snapshots(self):
		"""Get the history info from the server."""
		response = self.session.get(f"https://web.archive.org/cdx/search?limit=20&output=json&url=https://dl.appstreaming.autodesk.com/production/{self.os_id}/{self.app_id}/full.json")

		for v in response.json()[1:]:
			yield dict(zip(response.json()[0], v))

	@property
	def snapshot_versions(self):
		for snapshot in self.snapshots:
			full_json = self._get_full_json(snapshot["timestamp"])
			timestamp_dt = datetime.strptime(snapshot["timestamp"], "%Y%m%d%H%M%S")
			yield (timestamp_dt, full_json["build-version"])

		yield (datetime.now(), self.full_json["build-version"])

	@property
	def packages_info(self):
		if len(self.packages) != len(self.full_json["packages"]):
			self._get_packages()
		files = []
		for p in self.packages:
			files.append(p.info)
		return files

	@property
	def sub_applications_info(self):
		if len(self.sub_applications) != len(self.full_json["properties"]["sub-applications"]):
			self._get_sub_applications()
		sub_apps = []
		for p in self.sub_applications:
			sub_apps.append(p.info)
		return sub_apps

	def download(self, output_dir="data", recurse=True):
		"""Download the packages."""
		if len(self.packages) != len(self.full_json["packages"]):
			self._get_packages()

		for p in self.packages:
			p.download(self.session, output_dir)

		if recurse:
			for p in self.sub_applications:
				p.download(output_dir, recurse)

	def extract(self, output_dir="data", recurse=True):
		"""Extract the packages."""
		if len(self.packages) != len(self.full_json["packages"]):
			self._get_packages()

		for p in self.packages:
			p.extract(output_dir, recurse)

		if recurse:
			for p in self.sub_applications:
				p.extract(output_dir, recurse)

	def __str__(self) -> str:
		result = f"Application: {self.app_id} ({self.os_id})\n"
		for key, value in self.info.items():
			result += f"\t{key}: {value}\n"

		return result
