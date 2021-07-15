import requests
import json
import os
import uuid
import time

from urllib.parse import urljoin
from typing import Dict, Iterable, List, Any
from collections import OrderedDict
from graphql import (create_dictionary_item, create_document_plan, delete_dictionary_item, delete_document_plan,
                     dictionary, document_plan, document_plans, get_dictionary_item)


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
        r = requests.post(urljoin(self.host, '_graphql'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        return self._response(r)

    def generate(self, document_plan_name: str, data: Dict[str, Any], reader_model: Dict[str, bool] = None):
        body = {"documentPlanName": document_plan_name,
                "dataRow": data,
                "readerFlagValues": reader_model or self.default_reader_model,
                "async": False}
        r = requests.post(urljoin(self.host, 'nlg/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        return self._response(r)

    def generate_bulk(self, document_plan_name: str, data_rows: Iterable[Dict[str, Any]],
                      reader_model: Dict[str, bool] = None, result_format: str = 'raw'):
        body = {"documentPlanName": document_plan_name,
                "dataRows": OrderedDict([(str(uuid.uuid4()), row) for row in data_rows]),
                "readerFlagValues": reader_model or self.default_reader_model}
        r = requests.post(urljoin(self.host, 'nlg/_bulk/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        results = self._response(r)
        if type(results) == requests.Response:
            return results
        return (self.get_result(result_id, format=result_format) for result_id in body['dataRows'].keys())

    def get_result(self, id: str, format: str = 'raw'):
        result = None
        ready = False
        while not ready:
            r = requests.get(urljoin(self.host, f'nlg/{id}'), params={"format": format})
            result = self._response(r)
            if type(result) == requests.Response:
                return result
            elif result.get('error'):
                return result
            ready = result['ready']
            time.sleep(0.01)
        return result

    def delete_result(self, id: str):
        r = requests.delete(urljoin(self.host, f'nlg/{id}'))
        return self._response(r)

    def create_dictionary_item(self, key: str, category: str, forms: List[str],
                               language: str = "Eng", attributes: Dict[str, Any] = None):
        if not attributes:
            attributes = {}
        body = {"operationName": "createDictionaryItem",
                "query": create_dictionary_item,
                "variables": {"id": "_".join([key, category, language]),
                              "name": key,
                              "key": key,
                              "partOfSpeech": category,
                              "forms": forms,
                              "language": language,
                              "attributes": [{"name": k, "value": v} for k, v in attributes.items()]}}
        return self._graphql(body)

    def get_dictionary_item(self, id: str):
        body = {"operationName": "getDictionaryItem",
                "query": get_dictionary_item,
                "variables": {"dictionaryItemId": id}}
        return self._graphql(body)

    def delete_dictionary_item(self, id):
        body = {"operationName": "deleteDictionaryItem",
                "query": delete_dictionary_item,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_dictionary_items(self):
        body = {"operationName": "dictionary",
                "query": dictionary}
        return self._graphql(body)

    def get_document_plan(self, id: str = None, name: str = None):
        body = {"operationName": "documentPlan",
                "query": document_plan,
                "variables": {"id": id,
                              "name": name}}
        return self._graphql(body)

    def list_document_plans(self, kind: str = None, offset: int = 0, limit: int = 10000):
        body = {"operationName": "documentPlans",
                "query": document_plans,
                "variables": {"offset": offset,
                              "limit": limit,
                              "kind": kind}}
        return self._graphql(body)

    def create_document_plan(self, id: str, uid: str, name: str, kind: str, examples: List[str],
                             blockly_xml: str, document_plan: str):
        body = {"operationName": "createDocumentPlan",
                "query": create_document_plan,
                "variables": {"id": id,
                              "uid": uid,
                              "name": name,
                              "kind": kind,
                              "examples": examples,
                              "blocklyXml": blockly_xml,
                              "documentPlan": document_plan}}
        return self._graphql(body)

    def delete_document_plan(self, id: str):
        body = {"operationName": "deleteDocumentPlan",
                "query": delete_document_plan,
                "variables": {"id": id}}
        return self._graphql(body)
