import importlib
module = importlib.import_module('fbs_runtime._frozen')
module.BUILD_SETTINGS = {'app_name': 'yuki', 'author': 'Hal Long', 'version': '0.7.0', 'environment': 'local', 'excel_file_name': 'shot_info.xlsx', 'support_formats': ['mov', 'mp4', 'avi', 'mkv'], 'headers': ['thumbnail', 'duration', 'fps', 'resolution', 'frame_range']}