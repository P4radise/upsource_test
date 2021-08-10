import os


class Path:

    def __init__(self, filename):
        self.filename = filename

    def get(self):
        directory = os.getcwd()
        path = self.path_search(directory)
        if path is not None:
            return path

        while directory != '/':
            directory = os.path.split(directory)[0]
            path = self.path_search(directory)
            if path is not None:
                break

        return path

    def path_search(self, directory):
        path = None
        for dir_path, directories, files in os.walk(directory):
            if self.filename in files:
                path = os.path.join(dir_path, self.filename)
                break

        return path
