import os
import json

from CronIO.JsonReader import JSONReader
from CronIO.JsonWriter import JSONWriter


class Path:
    def __init__(self, _location, _is_remote=False):
        self.location = _location
        self.is_remote = _is_remote

    def isoformat(self):
        return {"location": self.location, "is_remote": self.is_remote}


# override JSON encoder for PathProvider data structure
class PathEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Path):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


# override JSON decoder for PathProvider data structure
class PathDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'location' in obj:
            return Path(obj.get('location'), obj.get('is_remote'))
        return obj


__pathes__file_name = "pathes.json"
pathes = dict()


def __set_to_defaults(root_location):
    global pathes
    pathes["TAB"] = Path(os.path.join(root_location, "tab.tab"))
    pathes["LOG"] = Path(os.path.join(root_location, "log"))
    pathes["SETTINGS"] = Path(os.path.join(root_location, "settings.json"))
    pathes["ANALYSIS"] = Path(os.path.join(root_location, "analysis"))


def __create_pathes():
    global pathes
    for key, path in pathes.items():
        if not os.path.exists(path.location):
            basename = os.path.basename(path.location)
            if basename.__contains__('.'):
                if not basename.__contains__(".tab"):
                    open(path.location, "x").close()
            else:
                os.mkdir(path.location)


def load():
    global pathes
    pathes["ROOT"] = Path(os.path.dirname(os.path.abspath(__file__)))
    root_location = pathes["ROOT"].location
    pathes_location = os.path.join(pathes["ROOT"].location, __pathes__file_name)

    if os.path.exists(pathes_location):
        pathes = JSONReader.read(pathes_location, PathDecoder)
        if pathes is None:
            __set_to_defaults(root_location)
        else:
            __create_pathes()
    else:
        __set_to_defaults(root_location)


def save():
    JSONWriter.write(pathes, os.path.join(pathes["ROOT"].location, __pathes__file_name), PathEncoder)

