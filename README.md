# Fusion 360 Streamer

This is a re-implementation of the `streamer.exe` application used by Fusion 360
(maybe from other Autodesk products too?) to install the application. The same
binary (just bundled with everything in a single exe) is used by the "Admin Install"
exe.

This software is completely unrelated to the Autodesk corporation and its subsidiaries
and is the product of reverse engineering (legal within the EU).

## Installation

All installation methods will install both the GUI and CLI versions of the software.
Just running the binary (or python module) will open the GUI and passing any arguments
will run the CLI version.

### All-in-one binary (recommended)

Download the single binary from the [releases page](https://github.com/dzervas/fusion360-streamer/releases)
for your operating system and run it.

### Python module

Install the python module with `pip install --upgrade --user fusion360-streamer`
and run it with `fusion360-streamer`.

### From source (for developers)

Clone the repository, use pipenv to install the dev dependencies and run `python -m fusion360_streamer`:

```bash
git clone https://github.com/dzervas/fusion360-streamer.git
cd fusion360-streamer
pipenv install --dev
pipenv shell
python -m fusion360_streamer
```

## Why did you write this?

The main reason is to add version history to Fusion 360. A daily GitHub workflow
is run which checks for a new version and if one exists stores all the links to
archive.org. That way safe versions of Fusion 360 can be downloaded and installed
that are no longer available on Autodesk's website.

It also serves as a much easier way to install Fusion 360 on Linux under wine.
