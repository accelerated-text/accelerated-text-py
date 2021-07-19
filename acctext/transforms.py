import json

from typing import Dict


def dictionary_item(x: Dict):
    if not x:
        return
    else:
        return {"id": x.get('id'),
                "key": x.get('name'),
                "forms": [phrase.get('text') for phrase in x.get('phrases', [])],
                "category": x.get('partOfSpeech'),
                "language": x.get('language'),
                "attributes": {attr.get('name'): attr.get('value') for attr in x.get('attributes', [])}}


def document_plan(x: Dict):
    if not x:
        return
    else:
        x['documentPlan'] = json.loads(x['documentPlan'])
        return x


def data_file(x: Dict):
    if not x:
        return
    else:
        return {"id": x['id'],
                "filename": x['fileName'],
                "header": x['fieldNames'],
                "rows": [[field['value'] for field in sorted(record['fields'],
                                                             key=lambda f: x['fieldNames'].index(f['fieldName']))]
                         for record in x['records']]}
