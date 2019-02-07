class FileWriter:

    @staticmethod
    def __write(obj, obj_location, mode):
        with open(obj_location, mode) as file_stream:
            file_stream.write(obj)

    @staticmethod
    def append(obj, obj_location):
        FileWriter.__write(obj, obj_location, 'a')

    @staticmethod
    def write(obj, obj_location):
        FileWriter.__write(obj, obj_location, 'w')
