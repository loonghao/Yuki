import os

from exe_builder.core import build_exe
from hz.toolkit import load_yaml

from src.config import APP_NAME, APP_VERSION, ROOT

data_list = []

data = load_yaml('{}/build.yaml'.format(ROOT), return_entity=True)

data_list.extend(data.data)
for dir_ in os.listdir(os.path.join(ROOT, 'resources')):
    data_list.append(
        '{1}/resources/{0}/*;resources/{0}'.format(dir_, ROOT))

build_exe('{}/main.py'.format(ROOT), APP_NAME,
          version=APP_VERSION,
          icon='{}/logo.ico'.format(ROOT),
          console=True, external=True, data=data_list)
