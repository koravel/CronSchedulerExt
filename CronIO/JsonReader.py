from CronIO.FileReader import FileReader
from CronIO.JsonSerializer import JSONSerializer


class JSONReader(FileReader):
    @staticmethod
    def read(obj_location, extended_decoder=None):
        return JSONSerializer.decode(FileReader.read(obj_location), extended_decoder)
