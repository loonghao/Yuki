# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""

# Import built-in modules
import os
import subprocess

# Import local modules
from yuki.config import APP_NAME, APP_VERSION, ROOT
from yuki.utils import get_temp_dir, load_yaml


# from config import APP_NAME, ROOT
def _make_command(file_path, name, work_path, version, console,
                  hooks,
                  release_dir, icon, external, data):
    root = os.path.dirname(file_path)
    if not version:
        version = os.getenv('BUILD_VERSION', '0.1.0.dev')
    command = [
        'pyinstaller',
        '--upx',
        os.path.join(ROOT, 'upx394w').replace('\\', '/'),
        '--name',
        name,
        '--clean',
        '-y',
        '--specpath',
        root,
        '--workpath',
        work_path
    ]
    if hooks:
        command.append('--additional-hooks-dir')
        command.append(hooks)
    if not console:
        command.append('--console')
    if external:
        command.append('-F')
    command.append(file_path.replace('\\', '/'))
    command.append('-i')
    if os.path.isfile(icon):
        command.append(icon)
    # else:
    #     command.append(HZResources.get_icon_resources(images))
    if not release_dir:
        release_dir = os.path.join(root, 'release', version)
    command.append('--distpath')
    command.append(release_dir)
    if data:
        for d in data:
            command.extend(
                ['--add-data', d.replace('\\', '/')])
    print(subprocess.list2cmdline(command))
    return subprocess.list2cmdline(command)


def build_exe(file_path,
              name,
              version=None,
              console=True,
              release_dir=None,
              icon='logo.ico',
              external=False,
              hooks=None,
              data=None):
    # temp = mkdtemp(prefix='exeBuilder_{}_'.format(name))
    if data is None:
        data = []
    temp = get_temp_dir()
    return subprocess.call(_make_command(file_path=file_path,
                                         name=name,
                                         version=version,
                                         console=console,
                                         release_dir=release_dir,
                                         icon=icon,
                                         hooks=hooks,
                                         external=external,
                                         data=data,
                                         work_path=temp))


if __name__ == '__main__':

    ROOT = os.path.dirname(__file__)
    data_list = []
    data = load_yaml('{}/build.yaml'.format(ROOT), return_entity=True)
    data_list.extend(data.data)
    for dir_ in os.listdir(os.path.join(ROOT, 'resources')):
        data_list.append(
            '{1}/resources/{0}/*;resources/{0}'.format(dir_, ROOT))
    build_py = os.path.join(ROOT, 'src', 'yuki', 'mian.py')
    build_exe(build_py, APP_NAME,
              version=APP_VERSION,
              icon='{}/logo.ico'.format(ROOT),
              console=True, external=True, data=data_list)
