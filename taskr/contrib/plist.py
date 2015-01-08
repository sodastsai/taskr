import plistlib
import six


class InfoPlist(object):

    def __init__(self, file_path, mode=None):
        self.file_path = file_path
        self.info_dict = {}
        self.mode = mode or 'r'

    def __getitem__(self, key):
        if key in self.info_dict:
            return self.info_dict[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.info_dict[key] = value

    def __delitem__(self, key):
        self.info_dict.pop(key, None)

    def __enter__(self):
        if 'r' in self.mode:
            with open(self.file_path, 'rb') as f:
                self.info_dict = plistlib.load(f) if six.PY3 else plistlib.readPlist(f)
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        if 'w' in self.mode:
            with open(self.file_path, 'wb') as f:
                if six.PY3:
                    plistlib.dump(self.info_dict, f)
                else:
                    plistlib.writePlist(self.info_dict, f)
