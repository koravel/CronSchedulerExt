from CronIO.JsonSerializer import JSONSerializer
from CronIO.FileWriter import FileWriter


class JSONWriter(FileWriter):
    @staticmethod
    def write(obj, obj_location, extended_encoder=None):
        FileWriter.write(JSONSerializer.encode(obj, extended_encoder), obj_location)

    @staticmethod
    def append(obj, obj_location, extended_encoder=None):
        raise NotImplementedError
