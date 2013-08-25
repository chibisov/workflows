# -*- coding: utf-8 -*-
import os
import json
import datetime
import unittest
from unittest import TestCase

from settings import SettingsBackend


class TestSettingsBackendFileAttribute(TestCase):
    def setUp(self):
        self.current_file_path = os.path.join(os.getcwd(), 'another_settings.json')
        self.settings = SettingsBackend(file_path=self.current_file_path)

    def test_file_name(self):
        self.assertEquals(self.settings.file_path, self.current_file_path)

    def test_should_use_current_dir_settings_json_file_by_default(self):
        settings = SettingsBackend()
        expected = os.path.join(os.getcwd(), 'settings.json')
        self.assertEquals(settings.file_path, expected)


class TestSettingsBackendDictBehaviour(TestCase):
    def setUp(self):
        self.tmp_file_path = '/tmp/test_settings.json'
        try:
            os.remove(self.tmp_file_path)
        except OSError:
            pass
        tmp_file = open(self.tmp_file_path, 'w')
        tmp_file.write('{"list_name": "Personal"}')
        tmp_file.close()

        self.settings = SettingsBackend(file_path=self.tmp_file_path)

    def test_get_key(self):
        self.assertTrue('list_name' in self.settings, "'list_name' should be existing key")

    def test_set_key(self):
        self.settings['another_setting'] = 'another value'
        self.assertEquals(self.settings['another_setting'], 'another value')

    def test_dict_comparison(self):
        self.settings['another_setting'] = 'another value'
        expected = {
            'list_name': 'Personal',
            'another_setting': 'another value'
        }
        self.assertEquals(self.settings, expected)

    def test_save(self):
        self.settings['another_setting'] = 'another value'
        stream = self.settings.save()
        expected = json.dumps({
            'list_name': 'Personal',
            'another_setting': 'another value'
        })
        self.assertEquals(open(self.tmp_file_path, 'r').read(), expected)

    def test_save_many_times(self):
        self.settings['another_setting'] = 'another value'
        self.settings.save()
        self.settings['moar_setting'] = 'moar value'
        self.settings.save()
        expected = json.dumps({
            'list_name': 'Personal',
            'another_setting': 'another value',
            'moar_setting': 'moar value'
        })
        self.assertEquals(open(self.tmp_file_path, 'r').read(), expected)

    def test_should_not_update_dict_if_json_decode_error(self):
        tmp_file = open(self.tmp_file_path, 'w')
        tmp_file.write('baaad json')
        tmp_file.close()

        try:
            self.settings = SettingsBackend(file_path=self.tmp_file_path)
        except ValueError:
            self.fail('should not raise exception, if could not decode json')

    def test_should_create_settings_file_if_it_is_not_exists(self):
        tmp_file_path = '/tmp/test_alfred_settings.json'
        try:
            os.remove(tmp_file_path)
        except OSError:
            pass

        try:
            settings_backend = SettingsBackend(file_path=tmp_file_path)
        except IOError:
            self.fail('should not fail, if file not exists')

        self.assertTrue(os.path.exists(tmp_file_path), 'should create file, if it is not exist')


if __name__ == '__main__':
    unittest.main()