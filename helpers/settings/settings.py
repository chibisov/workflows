import os
import json


class SettingsBackend(dict):
    """
    Usage:
        >> settings = SettingsBackend('/home/user/settings.json')
        >> settings['default_list'] = 'Personal'
        >> settings.save()  # flush json to /home/user/settings.json

        or without file_path current working directory would be used

        >> settings = SettingsBackend()
        >> print settings['default_list']
        Personal
    """
    def __init__(self, file_path=None):
        self.file_path = file_path or '{0}/settings.json'.format(os.getcwd())
        self.update(json.load(self._open(self.file_path)))

    def save(self):
        self._write(content=json.dumps(self))

    def _open(self, file_path, mode='r'):
        return open(file_path, mode)

    def _write(self, content):
        file_instance = self._open(self.file_path, 'w')
        file_instance.write(content)
        file_instance.close()