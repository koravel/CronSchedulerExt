import os
import json

from CronIO.JsonReader import JSONReader
from CronIO.JsonWriter import JSONWriter


class Route:
    def __init__(self, _location, _is_remote=False):
        self.location = _location
        self.is_remote = _is_remote

    def isoformat(self):
        return {"location": self.location, "is_remote": self.is_remote}


# override JSON encoder for Router data structure
class RouteEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Route):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


# override JSON decoder for Router data structure
class RouteDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'location' in obj:
            return Route(obj.get('location'), obj.get('is_remote'))
        return obj


__routes__file_name = "routes.json"
routes = dict()


def __set_to_defaults(root_location):
    routes["TAB"] = Route(os.path.join(root_location, "tab.tab"))
    routes["LOG"] = Route(os.path.join(root_location, "\\log"))
    routes["SETTINGS"] = Route(os.path.join(root_location, "settings.json"))
    routes["ANALYSIS"] = Route(os.path.join(root_location, "\\analysis"))


def __create_routes():
    global routes
    for key, route in routes.items():
        if not os.path.exists(route.location):
            if os.path.basename(route.location).__contains__('.'):
                open(route.location, "x").close()
            else:
                os.mkdir(route.location)


def load():
    global routes
    routes["ROOT"] = Route(os.path.dirname(os.path.abspath(__file__)))
    root_location = routes["ROOT"].location
    routes_location = os.path.join(routes["ROOT"].location, __routes__file_name)

    if os.path.exists(routes_location):
        routes = JSONReader.read(routes_location, RouteDecoder)
        if routes is None:
            __set_to_defaults(root_location)
        else:
            __create_routes()
    else:
        __set_to_defaults(root_location)


def save():
    JSONWriter.write(routes, os.path.join(routes["ROOT"].location, __routes__file_name), RouteEncoder)

