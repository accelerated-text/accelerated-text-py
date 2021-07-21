import requests
import json
import os
import uuid
import time
import edn_format

from urllib.parse import urljoin
from typing import Dict, Iterable, List, Any, Callable
from collections import OrderedDict
from zipfile import ZipFile

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

    def health(self) -> Dict:
        r = requests.get(urljoin(self.host, 'health'))
        return self._response(r)

    def status(self) -> Dict:
        r = requests.get(urljoin(self.host, 'status'))
        return self._response(r)

    def upload_data_file(self, path: str) -> Dict:
        filename = os.path.split(path)[-1]
        with open(path, 'rb') as file:
            r = requests.post(urljoin(self.host, 'accelerated-text-data-files/'), files={'file': (filename, file)})
        return self._response(r)

    def create_data_file(self, filename: str, header: Iterable[str], rows: Iterable[Iterable[Any]],
                         id: str = None) -> Dict:
        body = {"operationName": "createDataFile",
                "query": graphql.create_data_file,
                "variables": {"id": id or filename,
                              "filename": filename,
                              "content": transforms.data_file_to_csv({"header": header, "rows": rows})}}
        return self._graphql(body)

    def get_data_file(self, id: str, record_offset: int = 0, record_limit: int = 1000000000) -> Dict:
        body = {"operationName": "getDataFile",
                "query": graphql.get_data_file,
                "variables": {"id": id,
                              "recordOffset": record_offset,
                              "recordLimit": record_limit}}
        return self._graphql(body, transform=transforms.data_file)

    def list_data_files(self, offset: int = 0, limit: int = 1000, record_offset=0,
                        record_limit: int = 1000000000) -> Iterable[Dict]:
        body = {"operationName": "listDataFiles",
                "query": graphql.list_data_files,
                "variables": {"offset": offset,
                              "limit": limit,
                              "recordOffset": record_offset,
                              "recordLimit": record_limit}}
        return self._graphql(body, transform=lambda x: [transforms.data_file(f) for f in x['dataFiles']])

    def delete_data_file(self, id: str) -> Dict:
        body = {"id": id}
        r = requests.delete(urljoin(self.host, f'accelerated-text-data-files/'),
                            headers={"Content-Type": "application/json"},
                            data=json.dumps(body))
        return self._response(r)

    def generate(self, document_plan_name: str, data: Dict[str, Any], reader_model: Iterable[str] = None) -> Dict:
        body = {"documentPlanName": document_plan_name,
                "dataRow": data,
                "readerFlagValues": {reader: True for reader in reader_model or self.default_reader_model},
                "async": False}
        r = requests.post(urljoin(self.host, 'nlg/'),
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(body))
        return self._response(r)

    def generate_bulk(self, document_plan_name: str, data: Iterable[Dict[str, Any]],
                      reader_model: Iterable[str] = None) -> Iterable[Dict]:
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

    def get_result(self, id: str, format: str = 'raw') -> Dict:
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

    def delete_result(self, id: str) -> Dict:
        r = requests.delete(urljoin(self.host, f'nlg/{id}'))
        return self._response(r)

    def create_dictionary_item(self, key: str, category: str, forms: List[str], id: str = None,
                               language: str = "Eng", attributes: Dict[str, Any] = None) -> Dict:
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

    def get_dictionary_item(self, id: str) -> Dict:
        body = {"operationName": "getDictionaryItem",
                "query": graphql.get_dictionary_item,
                "variables": {"dictionaryItemId": id}}
        return self._graphql(body, transform=transforms.dictionary_item)

    def delete_dictionary_item(self, id: str) -> bool:
        body = {"operationName": "deleteDictionaryItem",
                "query": graphql.delete_dictionary_item,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_dictionary_items(self) -> Iterable[Dict]:
        body = {"operationName": "dictionary",
                "query": graphql.dictionary}
        return self._graphql(body, transform=lambda x: [transforms.dictionary_item(item) for item in x['items']])

    def get_document_plan(self, id: str = None, name: str = None) -> Dict:
        body = {"operationName": "documentPlan",
                "query": graphql.document_plan,
                "variables": {"id": id,
                              "name": name}}
        return self._graphql(body, transform=transforms.document_plan)

    def list_document_plans(self, kind: str = None, offset: int = 0, limit: int = 10000) -> Iterable[Dict]:
        body = {"operationName": "documentPlans",
                "query": graphql.document_plans,
                "variables": {"offset": offset,
                              "limit": limit,
                              "kind": kind}}
        return self._graphql(body, transform=lambda x: [transforms.document_plan(dp) for dp in x['items']])

    def create_document_plan(self, id: str, uid: str, name: str, kind: str, examples: List[str],
                             blocklyXml: str, documentPlan: Dict) -> Dict:
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

    def delete_document_plan(self, id: str) -> bool:
        body = {"operationName": "deleteDocumentPlan",
                "query": graphql.delete_document_plan,
                "variables": {"id": id}}
        return self._graphql(body)

    def get_language(self, id: str) -> Dict:
        body = {"operationName": "language",
                "query": graphql.language,
                "variables": {"id": id}}
        return self._graphql(body, transform=transforms.reader_flag)

    def add_language(self, id: str, name: str, flag: str = None, default: bool = False) -> Dict:
        body = {"operationName": "addLanguage",
                "query": graphql.add_language,
                "variables": {"id": id,
                              "name": name,
                              "flag": flag,
                              "defaultUsage": "YES" if default else "NO"}}
        return self._graphql(body, transform=transforms.reader_flag)

    def delete_language(self, id: str) -> bool:
        body = {"operationName": "deleteLanguage",
                "query": graphql.delete_language,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_languages(self) -> Iterable[Dict]:
        body = {"operationName": "languages",
                "query": graphql.languages}
        return self._graphql(body, transform=lambda x: [transforms.reader_flag(flag) for flag in x.get('flags', [])])

    def get_reader(self, id: str) -> Dict:
        body = {"operationName": "readerFlag",
                "query": graphql.reader_flag,
                "variables": {"id": id}}
        return self._graphql(body, transform=transforms.reader_flag)

    def create_reader(self, id: str, name: str, flag: str, default: bool = False) -> Dict:
        body = {"operationName": "createReaderFlag",
                "query": graphql.create_reader_flag,
                "variables": {"id": id,
                              "name": name,
                              "flag": flag,
                              "defaultUsage": "YES" if default else "NO"}}
        return self._graphql(body, transform=transforms.reader_flag)

    def delete_reader(self, id: str) -> bool:
        body = {"operationName": "deleteReaderFlag",
                "query": graphql.delete_reader_flag,
                "variables": {"id": id}}
        return self._graphql(body)

    def list_readers(self) -> Iterable[Dict]:
        body = {"operationName": "readerFlags",
                "query": graphql.reader_flags}
        return self._graphql(body, transform=lambda x: [transforms.reader_flag(flag) for flag in x.get('flags', [])])

    def clear_state(self):
        for lang in self.list_languages():
            if lang['id'] in self.default_reader_model:
                self.add_language(lang['id'], lang['name'], lang['flag'], True)
            else:
                self.delete_language(lang['id'])
        for reader in self.list_readers():
            if reader['id'] in self.default_reader_model:
                self.create_reader(reader['id'], reader['name'], reader['flag'], True)
            else:
                self.delete_reader(reader['id'])
        for dict_item in self.list_dictionary_items():
            self.delete_dictionary_item(dict_item['id'])
        for data_file in self.list_data_files():
            self.delete_data_file(data_file['id'])
        for document_plan in self.list_document_plans():
            self.delete_document_plan(document_plan['id'])

    def export_state(self, output_path: str, overwrite: bool = True):
        if overwrite and os.path.exists(output_path):
            os.remove(output_path)
        with ZipFile(output_path, 'a') as file:
            languages = [transforms.reader_flag_to_edn(language) for language in self.list_languages()]
            file.writestr('config/languages.edn', edn_format.dumps(languages, indent=4))
            readers = [transforms.reader_flag_to_edn(reader) for reader in self.list_readers()]
            file.writestr('config/readers.edn', edn_format.dumps(readers, indent=4))
            for document_plan in self.list_document_plans():
                file.writestr(f'document-plans/{document_plan["id"]}.json', json.dumps(document_plan, indent=4))
            dictionary = self.list_dictionary_items()
            file.writestr('dictionary/dictionary.edn', edn_format.dumps(dictionary, indent=4))
            for data_file in self.list_data_files():
                file.writestr(f'data-files/{data_file["filename"]}', transforms.data_file_to_csv(data_file))

    def restore_state(self, path: str):
        with ZipFile(path, 'r') as file:
            file_list = list(map(lambda x: x.filename, file.filelist))
            with file.open('config/languages.edn') as languages:
                for language in edn_format.loads(languages.read()):
                    self.add_language(**transforms.reader_flag_from_edn(language))
            with file.open('config/readers.edn') as readers:
                for reader in edn_format.loads(readers.read()):
                    self.create_reader(**transforms.reader_flag_from_edn(reader))
            for document_plan in filter(lambda x: x.startswith('document-plans'), file_list):
                with file.open(document_plan) as dp:
                    self.create_document_plan(**json.load(dp))
            for dictionary in filter(lambda x: x.startswith('dictionary'), file_list):
                with file.open(dictionary) as d:
                    for dict_item in edn_format.loads(d.read()):
                        self.create_dictionary_item(**transforms.dictionary_item_from_edn(dict_item))
            for data_file in filter(lambda x: x.startswith('data-files'), file_list):
                with file.open(data_file) as df:
                    filename = os.path.split(data_file)[-1]
                    self.create_data_file(**transforms.data_file_from_csv(filename, df.read()))
