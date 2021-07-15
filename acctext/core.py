import requests
import json
import os
import uuid
import time

from urllib.parse import urljoin
from typing import Dict, Iterable, Any
from collections import OrderedDict


class AcceleratedText:
    default_reader_model = {"Eng": True}

    def __init__(self, host: str = 'http://127.0.0.1:3001'):
        self.host = host

    def _response(self, r: requests.Response):
        if r.status_code in {200, 500}:
            return r.json()
        else:
            return r

    def health(self):
        r = requests.get(urljoin(self.host, 'health'))
        return self._response(r)

    def status(self):
        r = requests.get(urljoin(self.host, 'status'))
        return self._response(r)

    def upload_data(self, path: str):
        filename = os.path.split(path)[-1]
        with open(path, 'rb') as file:
            r = requests.post(urljoin(self.host, 'accelerated-text-data-files/'), files={'file': (filename, file)})
        return self._response(r)

    def _graphql(self, body: dict):
        r = requests.get(urljoin(self.host, '_graphql'),
                         headers={"Content-Type": "application/json"},
                         data=json.dumps(body))
        return self._response(r)

    def generate(self, document_plan: str, data: Dict[str, Any], reader_model: Dict[str, bool] = None):
        body = {"documentPlanName": document_plan,
                "dataRow": data,
                "readerFlagValues": reader_model or self.default_reader_model,
                "async": False}
        r = requests.post(urljoin(self.host, 'nlg/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        return self._response(r)

    def generate_bulk(self, document_plan: str, data_rows: Iterable[Dict[str, Any]],
                      reader_model: Dict[str, bool] = None, result_format: str = 'raw'):
        body = {"documentPlanName": document_plan,
                "dataRows": OrderedDict([(str(uuid.uuid4()), row) for row in data_rows]),
                "readerFlagValues": reader_model or self.default_reader_model}
        r = requests.post(urljoin(self.host, 'nlg/_bulk/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        results = self._response(r)
        if type(results) == requests.Response:
            return results
        return (self.get_result(result_id, result_format=result_format) for result_id in body['dataRows'].keys())

    def get_result(self, result_id: str, result_format: str = 'raw'):
        result = None
        ready = False
        while not ready:
            r = requests.get(urljoin(self.host, f'nlg/{result_id}'), params={"format": result_format})
            result = self._response(r)
            if type(result) == requests.Response:
                return result
            elif result.get('error'):
                return result
            ready = result['ready']
            time.sleep(0.01)
        return result

    def delete_result(self, result_id: str):
        r = requests.delete(urljoin(self.host, f'nlg/{result_id}'))
        return self._response(r)
