import asyncio
import json
from typing import Awaitable
from unittest import TestCase

from aioresponses import aioresponses

import hummingbot.connector.exchange.bitstamp.bitstamp_constants as CONSTANTS
from hummingbot.connector.exchange.bitstamp.bitstamp_web_utils import BitstampRESTPreProcessor
from hummingbot.connector.exchange.bitstamp import bitstamp_web_utils as web_utils
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest


class BitstampWebUtilsTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ev_loop = asyncio.get_event_loop()

    def async_run_with_timeout(self, coroutine: Awaitable, timeout: float = 1):
        ret = self.ev_loop.run_until_complete(asyncio.wait_for(coroutine, timeout))
        return ret

    def test_public_rest_url(self):
        path_url = "/TEST_PATH"
        domain = ""
        expected_url = CONSTANTS.REST_URL + CONSTANTS.API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.public_rest_url(path_url, domain))

    def test_private_rest_url(self):
        path_url = "/TEST_PATH"
        domain = ""
        expected_url = CONSTANTS.REST_URL + CONSTANTS.API_VERSION + path_url
        self.assertEqual(expected_url, web_utils.private_rest_url(path_url, domain))

    @aioresponses()
    def test_get_current_server_time(self, mock_api: aioresponses):
        response = { "server_time": 1719431075066 }
        url = web_utils.public_rest_url(CONSTANTS.STATUS_URL)
        mock_api.get(url, body=json.dumps(response))

        time = self.async_run_with_timeout(web_utils.get_current_server_time())

        self.assertEqual(response["server_time"], time)

    def test_bitstamp_rest_pre_processor_with_data(self):
        payload = {"test": "data"}
        request = RESTRequest(method=RESTMethod.POST, data=json.dumps({"test": "data"}), headers={"Content-Type": "application/json"})
        pre_processor = BitstampRESTPreProcessor()

        request = self.async_run_with_timeout(pre_processor.pre_process(request))

        self.assertEqual(request.headers["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(payload, request.data)

    def test_bitstamp_rest_pre_processor_without_data(self):
        request = RESTRequest(method=RESTMethod.POST, data=None, headers={"Content-Type": "application/json"})
        pre_processor = BitstampRESTPreProcessor()

        request = self.async_run_with_timeout(pre_processor.pre_process(request))

        self.assertEqual(request.headers["Content-Type"], "")
        self.assertIsNone(request.data)
        