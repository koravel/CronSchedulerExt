class FileReader:

    @staticmethod
    def read(obj_location):
        with open(obj_location, 'r') as file_stream:
            return file_stream.read()


