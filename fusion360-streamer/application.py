from .constants import FUSION360_APPID, WINDOWS_OSID, APPLICATION_JSON_URL, PACKAGE_JSON_URL, ARCHIVE_GET_URL, ARCHIVE_SAVE_URL, ARCHIVE_SEARCH_URL
from .package import Package
from datetime import datetime
from humanize import naturalsize
import requests



class Application():
	os_id: str = WINDOWS_OSID
	app_id: str = FUSION360_APPID
	session: requests.Session = None
	full_json: dict = None
	packages: list[Package] = []
	# sub_applications = []

	def __init__(self, app_id=FUSION360_APPID, os_id=WINDOWS_OSID, session=requests.Session(), archive_timestamp=None):
		self.app_id = app_id
		self.os_id = os_id
		self.session = session
		self.sub_applications = []
		self.full_json = self._get_full_json(archive_timestamp)

	def _get_full_json(self, archive_timestamp=None) -> dict:
		"""Get the streamer url from the server."""

		response = None
		url = APPLICATION_JSON_URL.format(self.os_id, self.app_id)
		if archive_timestamp is not None:
			response = self.session.get(ARCHIVE_GET_URL.format(archive_timestamp, url))
		else:
			response = self.session.get(url)

		return response.json()

	def _get_packages(self, archive=False) -> None:
		for p in self.full_json["packages"]:
			print("Getting package JSON", p['checksum'])

			url = PACKAGE_JSON_URL.format(p['checksum'])
			if archive:
				self.session.get(ARCHIVE_SAVE_URL.format(url))
				print("\tArchived")

			response = self.session.get(url)
			self.packages.append(Package(response.json()))

	def _get_sub_applications(self) -> None:
		print("\t>>>", self.app_id)
		if "sub-applications" not in self.full_json["properties"]:
			self.sub_applications = []
			return

		for p in self.full_json["properties"]["sub-applications"]:
			self.sub_applications.append(Application(p, self.os_id, self.session))

	def _store_to_archive_if_required(self) -> None:
		"""Store the full.json to the archive if it is not already there."""
		versions = self.available_versions(2)

		archive_version = next(versions)[1]
		try:
			current_version = next(versions)[1]
		except StopIteration:
			current_version = archive_version
			archive_version = None

		if archive_version != current_version:
			print("Storing version", current_version, "of application", self.full_json["properties"]["display-name"])
			self.session.get(ARCHIVE_SAVE_URL.format(APPLICATION_JSON_URL.format(self.os_id, self.app_id)))

			self._get_packages(True)
			for p in self.packages:
				print("Storing package", p.source_id, "to archive")
				p._store_to_archive_if_required(self.session)
		else:
			print("Version", current_version, "of application", self.full_json["properties"]["display-name"], "already in archive (assuming packages are already there too)")

		print("--- Sub-applications ---")
		self._get_sub_applications()
		for a in self.sub_applications:
			print("\tStoring sub-application", a.full_json["properties"]["display-name"], "to archive")
			a._store_to_archive_if_required()

	@property
	def info(self) -> dict:
		"""Get the current version info from the server."""

		return {
			"display-name": self.full_json["properties"]["display-name"],
			"required-os": self.full_json["properties"]["required-os"]["friendly-version"] if "required-os" in self.full_json["properties"] else None,
			"build-version": self.full_json["build-version"],
			"major-update-version": self.full_json["major-update-version"] if "major-update-version" in self.full_json else None,
			"patches_build_version": self.full_json["patches_build_version"],
			"sub-applications": self.full_json["properties"]["sub-applications"] if "sub-applications" in self.full_json["properties"] else None,
		}

	def snapshots(self, limit=20) -> list[dict]:
		"""Get the history info from the server."""

		response = self.session.get(ARCHIVE_SEARCH_URL.format(limit, APPLICATION_JSON_URL.format(self.os_id, self.app_id)))

		for v in response.json()[1:]:
			yield dict(zip(response.json()[0], v))

	def available_versions(self, limit=20) -> list[tuple[datetime, str]]:
		last_version = None
		if limit > 1:
			for snapshot in self.snapshots(limit - 1):
				full_json = self._get_full_json(snapshot["timestamp"])
				timestamp_dt = datetime.strptime(snapshot["timestamp"], "%Y%m%d%H%M%S")
				last_version = full_json["build-version"]
				yield (timestamp_dt, full_json["build-version"])

		if last_version != self.full_json["build-version"]:
			yield (datetime.now(), self.full_json["build-version"])

	@property
	def packages_info(self) -> list[dict]:
		if len(self.packages) != len(self.full_json["packages"]):
			self._get_packages()

		for p in self.packages:
			yield p.info

	@property
	def sub_applications_info(self) -> list[dict]:
		if len(self.sub_applications) != len(self.full_json["properties"]["sub-applications"]):
			self._get_sub_applications()

		for p in self.sub_applications:
			yield p.info

	def download(self, output_dir="data", recurse=True) -> None:
		"""Download the packages."""
		if len(self.packages) != len(self.full_json["packages"]):
			self._get_packages()

		for p in self.packages:
			p.download(self.session, output_dir)

		if recurse:
			for p in self.sub_applications:
				p.download(output_dir, recurse)

	def extract(self, output_dir="data", recurse=True) -> None:
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
