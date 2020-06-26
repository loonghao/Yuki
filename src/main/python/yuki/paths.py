import os


def ensure_paths(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def get_file_ext(path):
    if os.path.splitext(path)[1]:
        ext = os.path.splitext(path)[1]
        ext = ext.replace(".", "")
        return ext
    else:
        return ""
