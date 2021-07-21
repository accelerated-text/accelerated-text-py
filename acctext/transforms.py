import json
import edn_format
import io
import csv

from typing import Dict


def dictionary_item(x: Dict) -> Dict:
    return {"id": x.get('id'),
            "key": x.get('name'),
            "forms": [phrase.get('text') for phrase in x.get('phrases', [])],
            "category": x.get('partOfSpeech'),
            "language": x.get('language'),
            "attributes": {attr.get('name'): attr.get('value') for attr in x.get('attributes', [])}}


def dictionary_item_from_edn(x: Dict) -> Dict:
    return {"id": x['id'],
            "key": x['key'],
            "forms": list(x['forms']),
            "category": x['category'],
            "language": x['language'],
            "attributes": dict(x['attributes'])}


def document_plan(x: Dict) -> Dict:
    x['documentPlan'] = json.loads(x['documentPlan'])
    return x


def data_file(x: Dict) -> Dict:
    return {"id": x['id'],
            "filename": x['fileName'],
            "header": x['fieldNames'],
            "rows": [[field['value'] for field in sorted(record['fields'],
                                                         key=lambda f: x['fieldNames'].index(f['fieldName']))]
                     for record in x['records']]}


def data_file_to_csv(x: Dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(x['header'])
    for row in x['rows']:
        writer.writerow(row)
    return output.getvalue()


def data_file_from_csv(filename: str, x: bytes) -> Dict:
    f = io.StringIO(x.decode('utf-8'))
    rows = list(csv.reader(f, delimiter=','))
    return {"id": filename,
            "filename": filename,
            "header": rows[0],
            "rows": rows[1:]}


def reader_flag(x: Dict) -> Dict:
    return {'id': x['id'],
            'name': x['name'],
            'flag': x['flag'],
            'default': x['defaultUsage'] == 'YES'}


def reader_flag_to_edn(x: Dict) -> Dict:
    return {edn_format.Keyword('data.spec.reader-model/code'): x['id'],
            edn_format.Keyword('data.spec.reader-model/flag'): x['flag'],
            edn_format.Keyword('data.spec.reader-model/name'): x['name'],
            edn_format.Keyword('data.spec.reader-model/available?'): True,
            edn_format.Keyword('data.spec.reader-model/enabled?'): x['default']}


def reader_flag_from_edn(x: Dict) -> Dict:
    return {"id": x[edn_format.Keyword('data.spec.reader-model/code')],
            'name': x[edn_format.Keyword('data.spec.reader-model/name')],
            'flag': x[edn_format.Keyword('data.spec.reader-model/flag')],
            'default': x[edn_format.Keyword('data.spec.reader-model/enabled?')]}
