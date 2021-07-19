import requests
import json
import os
import uuid
import time

from urllib.parse import urljoin
from typing import Dict, Iterable, List, Any, Callable
from collections import OrderedDict
from acctext import graphql, transforms


class AcceleratedText:
    default_reader_model = {"Eng": True}

    def __init__(self, host: str = 'http://127.0.0.1:3001'):
        self.host = host

    def _response(self, r: requests.Response):
        if r.status_code in {200, 500}:
            return r.json()
        else:
            return r

    def _graphql(self, body: dict, transform: Callable = None):
        r = requests.post(urljoin(self.host, '_graphql'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        r = self._response(r)
        if type(r) == requests.Response:
            return r
        elif 'errors' in r:
            raise Exception(r['errors'])
        else:
            keys = list(r['data'].keys())
            data = r['data'][keys[0]] if len(keys) == 1 else r['data']
            return transform(data) if transform else data

    def health(self):
        r = requests.get(urljoin(self.host, 'health'))
        return self._response(r)

    def status(self):
        r = requests.get(urljoin(self.host, 'status'))
        return self._response(r)

    def upload_data_file(self, path: str):
        filename = os.path.split(path)[-1]
        with open(path, 'rb') as file:
            r = requests.post(urljoin(self.host, 'accelerated-text-data-files/'), files={'file': (filename, file)})
        return self._response(r)

    def delete_data_file(self, id: str):
        body = {"id": id}
        r = requests.delete(urljoin(self.host, f'accelerated-text-data-files/'),
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

    def generate_bulk(self, document_plan_name: str, data: Iterable[Dict[str, Any]],
                      reader_model: Dict[str, bool] = None):
        body = {"documentPlanName": document_plan_name,
                "dataRows": OrderedDict([(str(uuid.uuid4()), row) for row in data]),
                "readerFlagValues": reader_model or self.default_reader_model}
        r = requests.post(urljoin(self.host, 'nlg/_bulk/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        results = self._response(r)
        if type(results) == requests.Response:
            return results
        return (self.get_result(result_id) for result_id in body['dataRows'].keys())

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
                               id: str = None, language: str = "Eng", attributes: Dict[str, Any] = None):
        if not attributes:
            attributes = {}
        body = {"operationName": "createDictionaryItem",
                "query": graphql.create_dictionary_item,
                "variables": {"id": id or "_".join([key, category, language]),
                              "name": key,
                              "key": key,
                              "partOfSpeech": category,
                              "forms": forms,
                              "language": language,
                              "attributes": [{"name": k, "value": v} for k, v in attributes.items()]}}
        return self._graphql(body, transform=transforms.dictionary_item)

    def get_dictionary_item(self, id: str):
        body = {"operationName": "getDictionaryItem",
                "query": graphql.get_dictionary_item,
                "variables": {"dictionaryItemId": id}}
        return self._graphql(body, transform=transforms.dictionary_item)

    def delete_dictionary_item(self, id):
        body = {"operationName": "deleteDictionaryItem",
                "query": graphql.delete_dictionary_item,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_dictionary_items(self):
        body = {"operationName": "dictionary",
                "query": graphql.dictionary}
        return self._graphql(body, transform=lambda x: [transforms.dictionary_item(item) for item in x['items']])

    def get_document_plan(self, id: str = None, name: str = None):
        body = {"operationName": "documentPlan",
                "query": graphql.document_plan,
                "variables": {"id": id,
                              "name": name}}
        return self._graphql(body, transform=transforms.document_plan)

    def list_document_plans(self, kind: str = None, offset: int = 0, limit: int = 10000):
        body = {"operationName": "documentPlans",
                "query": graphql.document_plans,
                "variables": {"offset": offset,
                              "limit": limit,
                              "kind": kind}}
        return self._graphql(body, transform=lambda x: [transforms.document_plan(dp) for dp in x['items']])

    def create_document_plan(self, id: str, uid: str, name: str, kind: str, examples: List[str],
                             blocklyXml: str, documentPlan: Dict):
        body = {"operationName": "createDocumentPlan",
                "query": graphql.create_document_plan,
                "variables": {"id": id,
                              "uid": uid,
                              "name": name,
                              "kind": kind,
                              "examples": examples,
                              "blocklyXml": blocklyXml,
                              "documentPlan": json.dumps(documentPlan)}}
        return self._graphql(body, transform=transforms.document_plan)

    def delete_document_plan(self, id: str):
        body = {"operationName": "deleteDocumentPlan",
                "query": graphql.delete_document_plan,
                "variables": {"id": id}}
        return self._graphql(body)
