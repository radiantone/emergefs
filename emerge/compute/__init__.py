import sys

from emerge.core.objects import File


class Data(File):
    def set_data(self, data):
        self.data = data

    def get_size(self):
        return sys.getsizeof(self.data)
