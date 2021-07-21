import requests
import json
import os
import uuid
import time
import io
import csv

from urllib.parse import urljoin
from typing import Dict, Iterable, List, Any, Callable
from collections import OrderedDict
from acctext import graphql, transforms


class AcceleratedText:
    default_reader_model = ["Eng"]

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

    def create_data_file(self, filename: str, header: Iterable[str], rows: Iterable[Iterable[Any]], id: str = None):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
        body = {"operationName": "createDataFile",
                "query": graphql.create_data_file,
                "variables": {"id": id or filename,
                              "filename": filename,
                              "content": output.getvalue()}}
        return self._graphql(body)

    def get_data_file(self, id: str, record_offset: int = 0, record_limit: int = 1000000000):
        body = {"operationName": "getDataFile",
                "query": graphql.get_data_file,
                "variables": {"id": id,
                              "recordOffset": record_offset,
                              "recordLimit": record_limit}}
        return self._graphql(body, transform=transforms.data_file)

    def list_data_files(self, offset: int = 0, limit: int = 1000, record_offset=0, record_limit: int = 1000000000):
        body = {"operationName": "listDataFiles",
                "query": graphql.list_data_files,
                "variables": {"offset": offset,
                              "limit": limit,
                              "recordOffset": record_offset,
                              "recordLimit": record_limit}}
        return self._graphql(body, transform=lambda x: [transforms.data_file(f) for f in x['dataFiles']])

    def delete_data_file(self, id: str):
        body = {"id": id}
        r = requests.delete(urljoin(self.host, f'accelerated-text-data-files/'),
                            headers={"Content-Type": "application/json"},
                            data=json.dumps(body))
        return self._response(r)

    def generate(self, document_plan_name: str, data: Dict[str, Any], reader_model: Iterable[str] = None):
        body = {"documentPlanName": document_plan_name,
                "dataRow": data,
                "readerFlagValues": {reader: True for reader in reader_model or self.default_reader_model},
                "async": False}
        r = requests.post(urljoin(self.host, 'nlg/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        return self._response(r)

    def generate_bulk(self, document_plan_name: str, data: Iterable[Dict[str, Any]],
                      reader_model: Iterable[str] = None):
        body = {"documentPlanName": document_plan_name,
                "dataRows": OrderedDict([(str(uuid.uuid4()), row) for row in data]),
                "readerFlagValues": {reader: True for reader in reader_model or self.default_reader_model}}
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

    def delete_dictionary_item(self, id: str):
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

    def get_language(self, id: str):
        body = {"operationName": "language",
                "query": graphql.language,
                "variables": {"id": id}}
        return self._graphql(body, transform=transforms.reader_flag)

    def add_language(self, id: str, name: str, flag: str = None, default: bool = False):
        body = {"operationName": "addLanguage",
                "query": graphql.add_language,
                "variables": {"id": id,
                              "name": name,
                              "flag": flag,
                              "defaultUsage": "YES" if default else "NO"}}
        return self._graphql(body, transform=transforms.reader_flag)

    def delete_language(self, id: str):
        body = {"operationName": "deleteLanguage",
                "query": graphql.delete_language,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_languages(self):
        body = {"operationName": "languages",
                "query": graphql.languages}
        return self._graphql(body, transform=lambda x: [transforms.reader_flag(flag) for flag in x.get('flags', [])])

    def get_reader(self, id: str):
        body = {"operationName": "readerFlag",
                "query": graphql.reader_flag,
                "variables": {"id": id}}
        return self._graphql(body, transform=transforms.reader_flag)

    def create_reader(self, id: str, name: str, flag: str, default: bool = False):
        body = {"operationName": "createReaderFlag",
                "query": graphql.create_reader_flag,
                "variables": {"id": id,
                              "name": name,
                              "flag": flag,
                              "defaultUsage": "YES" if default else "NO"}}
        return self._graphql(body, transform=transforms.reader_flag)

    def delete_reader(self, id: str):
        body = {"operationName": "deleteReaderFlag",
                "query": graphql.delete_reader_flag,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_readers(self):
        body = {"operationName": "readerFlags",
                "query": graphql.reader_flags}
        return self._graphql(body, transform=lambda x: [transforms.reader_flag(flag) for flag in x.get('flags', [])])
