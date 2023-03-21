FUSION360_APPID = "73e72ada57b7480280f7a6f4a289729f"
WINDOWS_OSID = "67316f5e79bc48318aa5f7b6bb58243d"
OSX_OSID = "97e6dd95735340d6ad6e222a520454db"

OSIDS = {
	"windows": WINDOWS_OSID,
	"osx": OSX_OSID,
}

APPIDS = {
	"fusion360": FUSION360_APPID,
}

# URLs
APPLICATION_JSON_URL = "https://dl.appstreaming.autodesk.com/production/{}/{}/full.json"
PACKAGE_JSON_URL = "https://dl.appstreaming.autodesk.com/production/packages/{}.json"
PACKAGE_TAR_URL = "https://dl.appstreaming.autodesk.com/production/packages/{}.tar"
ARCHIVE_GET_URL = "https://web.archive.org/web/{}/{}"
ARCHIVE_SAVE_URL = "https://web.archive.org/save/{}"
ARCHIVE_SEARCH_URL = "https://web.archive.org/cdx/search?limit=-{}&output=json&url={}"
ARCHIVE_AVAILABILITY_URL = "https://archive.org/wayback/available?closest=now&url={}"
