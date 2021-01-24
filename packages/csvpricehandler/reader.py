from file_read_backwards import FileReadBackwards


class Reader():

    def __init__(self, file_path):

        self.file_path = file_path
        self.resource = FileReadBackwards(file_path, encoding="utf-8")

    def next(self):

        return self.resource.readline()
