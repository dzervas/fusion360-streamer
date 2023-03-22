# Fusion 360 Streamer

This is a re-implementation of the `streamer.exe` application used by Fusion 360
(maybe from other Autodesk products too?) to install the application. The same
binary (just bundled with everything in a single exe) is used by the "Admin Install"
exe.

This software is completely unrelated to the Autodesk corporation and its subsidiaries
and is the product of reverse engineering (legal within the EU).

## Why did you write this?

The main reason is to add version history to Fusion 360. A daily GitHub workflow
is run which checks for a new version and if one exists stores all the links to
archive.org. That way safe versions of Fusion 360 can be downloaded and installed
that are no longer available on Autodesk's website.

It also serves as a much easier way to install Fusion 360 on Linux under wine.
