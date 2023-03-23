from fusion360_streamer.constants import PACKAGE_TAR_URL, ARCHIVE_GET_URL, ARCHIVE_SAVE_URL
from hashlib import sha1
from humanize import naturalsize
import os
import tarfile


def sha1sum(filename):
	h = sha1()
	b = bytearray(128*1024)
	mv = memoryview(b)
	with open(filename, 'rb', buffering=0) as f:
		while n := f.readinto(mv):
			h.update(mv[:n])
	return h.hexdigest()


class Package():
	source_id: str
	size: str
	destination: str
	_cfg_src: str
	json: dict

	def __init__(self, package_json):
		self.json = package_json
		self.source_id = package_json["properties"]["source-id"] if "source-id" in package_json["properties"] else "Unknown"
		self.size = naturalsize(package_json["properties"]["size"]) if "size" in package_json["properties"] else "Unknown"
		self._cfg_src = package_json["properties"]["_cfg-src"] if "_cfg-src" in package_json["properties"] else "Unknown"
		self.destination = package_json["properties"]["destination"] if "destination" in package_json["properties"] else "Unknown"

	@property
	def info(self) -> dict:
		return {
			"source-id": self.source_id,
			"size": self.size,
			"destination": self.destination,
			"_cfg-src": self._cfg_src,
		}

	def _store_to_archive_if_required(self, session) -> None:
		"""Store the package to the archive if it is not already there."""
		if "non-patched" not in self.json:
			print("Skipping package", self.source_id, "as it has no non-patched files.")
			print("JSON:", self.json)
			return

		for f in self.json["non-patched"]:
			file = f + ".tar.xz"
			session.get(ARCHIVE_SAVE_URL.format(PACKAGE_TAR_URL.format(file)))

	def download(self, session, output_dir, timestamp=None) -> None:
		"""Download the package to a destination."""
		if "non-patched" not in self.json:
			print("Skipping package", self.source_id, "as it has no non-patched files.")
			print("JSON:", self.json)
			return

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		for f in self.json["non-patched"]:
			file = f + ".tar.xz"

			if os.path.exists(os.path.join(output_dir, file)) and sha1sum(os.path.join(output_dir, file)) == f:
				print("Skipping downloaded and checked package", file)
				continue

			print("Downloading package", file)
			if timestamp:
				response = session.get(ARCHIVE_GET_URL.format(timestamp, PACKAGE_TAR_URL.format(file)))
			else:
				response = session.get(PACKAGE_TAR_URL.format(file))

			with open(os.path.join(output_dir, file), "wb") as f:
				f.write(response.content)

	def extract(self, output_dir) -> None:
		if "non-patched" not in self.json:
			print("Skipping package", self.source_id, "as it has no non-patched files.")
			print("JSON:", self.json)
			return

		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		for f in self.json["non-patched"]:
			file = f + ".tar.xz"

			dest = os.path.join(output_dir, "extracted", self.destination)
			if not os.path.exists(dest):
				os.makedirs(dest)

			print("Extracting package", file)
			with tarfile.open(os.path.join(output_dir, file), "r:xz") as tar:
				tar.extractall(dest)

	def __str__(self) -> str:
		return f"Package: {self.source_id} ({self.size})"
