import pytest
import json
import unittest
from unittest.mock import Mock, MagicMock, patch, call

from DeviceManager.DatabaseModels import DeviceTemplate
from DeviceManager.TemplateHandler import TemplateHandler, attr_format, paginate
from DeviceManager.utils import HTTPRequestError

from .token_test_generator import generate_token

from alchemy_mock.mocking import AlchemyMagicMock, UnifiedAlchemyMagicMock


class TestTemplateHandler(unittest.TestCase):

    @patch('DeviceManager.TemplateHandler.db')
    def test_get_templates(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        params_query = {'page_number': 5, 'per_page': 1,
                        'sortBy': None, 'attr': [], 'attr_type': [], 'label': 'dummy'}
        result = TemplateHandler.get_templates(params_query, token)
        self.assertIsNotNone(result)

        # test using attrs
        params_query = {'page_number': 1, 'per_page': 1,
                        'sortBy': None, 'attr': ['foo=bar'], 'attr_type': []}
        result = TemplateHandler.get_templates(params_query, token)
        self.assertIsNotNone(result)

        # test using sortBy
        params_query = {'page_number': 1, 'per_page': 1,
                        'sortBy': 'label', 'attr': ['foo=bar'], 'attr_type': []}
        result = TemplateHandler.get_templates(params_query, token)
        self.assertIsNotNone(result)

        # test without querys
        params_query = {'page_number': 5, 'per_page': 1,
                        'sortBy': None, 'attr': [], 'attr_type': []}
        result = TemplateHandler.get_templates(params_query, token)
        self.assertIsNotNone(result)

    @patch('DeviceManager.TemplateHandler.db')
    def test_create_tempĺate(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        data = """{
            "label": "SensorModel",
            "attrs": [
                {
                    "label": "temperature",
                    "type": "dynamic",
                    "value_type": "float"
                },
                {
                    "label": "model-id",
                    "type": "static",
                    "value_type": "string",
                    "static_value": "model-001"
                }
            ]
        }"""

        params_query = {'content_type': 'application/json', 'data': data}
        result = TemplateHandler.create_template(params_query, token)
        self.assertIsNotNone(result)
        self.assertEqual(result['result'], 'ok')
        self.assertIsNotNone(result['template'])

    @patch('DeviceManager.TemplateHandler.db')
    def test_get_template(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        template = DeviceTemplate(id=1, label='template1')
        params_query = {'attr_format': 'both'}

        with patch('DeviceManager.TemplateHandler.assert_template_exists') as mock_template_exist_wrapper:
            mock_template_exist_wrapper.return_value = template
            result = TemplateHandler.get_template(params_query, 'template_id_test', token)
            self.assertIsNotNone(result)

            mock_template_exist_wrapper.return_value = None
            result = TemplateHandler.get_template(params_query, 'template_id_test', token)
            self.assertFalse(result)

    @patch('DeviceManager.TemplateHandler.db')
    def test_delete_all_templates(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        result = TemplateHandler.delete_all_templates(token)
        self.assertIsNotNone(result)
        self.assertTrue(result)
        self.assertEqual(result['result'], 'ok')


    @patch('DeviceManager.TemplateHandler.db')
    def test_remove_template(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        template = DeviceTemplate(id=1, label='template1')

        with patch('DeviceManager.TemplateHandler.assert_template_exists') as mock_template_exist_wrapper:
            mock_template_exist_wrapper.return_value = template

            result = TemplateHandler.remove_template(1, token)
            self.assertIsNotNone(result)
            self.assertTrue(result)
            self.assertTrue(result['removed'])
            self.assertEqual(result['result'], 'ok')

    @patch('DeviceManager.TemplateHandler.db')
    def test_update_template(self, db_mock):
        db_mock.session = AlchemyMagicMock()
        token = generate_token()

        template = DeviceTemplate(id=1, label='SensorModel')

        data = """{
            "label": "SensorModelUpdated",
            "attrs": [
                {
                    "label": "temperature",
                    "type": "dynamic",
                    "value_type": "float"
                },
                {
                    "label": "model-id",
                    "type": "static",
                    "value_type": "string",
                    "static_value": "model-001"
                }
            ]
        }"""

        params_query = {'content_type': 'application/json', 'data': data}

        with patch('DeviceManager.TemplateHandler.assert_template_exists') as mock_template_exist_wrapper:
            mock_template_exist_wrapper.return_value = template

            with patch.object(TemplateHandler, "verifyInstance", return_value=MagicMock()):
                result = TemplateHandler.update_template(params_query, 1, token)
                self.assertIsNotNone(result)
                self.assertTrue(result)
                self.assertTrue(result['updated'])
                self.assertEqual(result['result'], 'ok')

    def test_verify_intance_kafka(self):
         with patch('DeviceManager.TemplateHandler.KafkaHandler') as mock_kafka_instance_wrapper:
             mock_kafka_instance_wrapper.return_value = Mock()
             self.assertIsNotNone(TemplateHandler.verifyInstance(None))

    def test_attr_format(self):
        params = {'data_attrs': [], 'config_attrs': [], 'id': 1, 'attrs': [], 'label': 'template1'}

        result = attr_format('split', params)
        self.assertNotIn('attrs', result)

        result = attr_format('single', params)
        self.assertNotIn('config_attrs', result)
        self.assertNotIn('data_attrs', result)

    @patch('DeviceManager.TemplateHandler.db')
    def test_paginate(self, db_mock):
        db_mock.session = AlchemyMagicMock()

        result = paginate(db_mock.session.query, 0, 10, True)
        self.assertIsNone(result)
       
