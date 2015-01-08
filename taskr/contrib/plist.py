import plistlib
import six


class Plist(object):

    def __init__(self, file_path, mode=None):
        self.file_path = file_path
        self.content_dict = {}
        self.mode = mode or 'r'

    def __getitem__(self, key):
        if key in self.content_dict:
            return self.content_dict[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.content_dict[key] = value

    def __delitem__(self, key):
        self.content_dict.pop(key, None)

    def __enter__(self):
        if 'r' in self.mode:
            with open(self.file_path, 'rb') as f:
                self.content_dict = plistlib.load(f) if six.PY3 else plistlib.readPlist(f)
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        if 'w' in self.mode:
            with open(self.file_path, 'wb') as f:
                if six.PY3:
                    plistlib.dump(self.content_dict, f)
                else:
                    plistlib.writePlist(self.content_dict, f)
