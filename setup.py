#!/usr/bin/env python

import fusion360_streamer
from setuptools import setup
import json
import os

# Load requirements from Pipfile.lock
lockfile = os.path.join(os.path.dirname(__file__), 'Pipfile.lock')
with open(lockfile) as f:
	lock_data = json.load(f)

requirements = [package_name + package_data["version"] for package_name, package_data in lock_data['default'].items()]


setup(
	name="fusion360-streamer",
	version=fusion360_streamer.__version__,
	description="Autodesk Fusion 360 Streamer python implementation",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	author="Dimitris Zervas",
	author_email="dzervas@dzervas.gr",
	url="https://github.com/dzervas/fusion360-streamer",
	license="GPLv3",
	packages=["fusion360_streamer"],
	install_requires=requirements,
	entry_points={
		"console_scripts": [
			"fusion360-streamer=fusion360_streamer.__main__:main",
		],
	},
)
