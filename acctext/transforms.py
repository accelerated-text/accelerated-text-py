from typing import Dict


def dictionary_item(x: Dict):
    return {"id": x.get('id'),
            "key": x.get('name'),
            "forms": [phrase.get('text') for phrase in x.get('phrases', [])],
            "category": x.get('partOfSpeech'),
            "language": x.get('language'),
            "attributes": {attr.get('name'): attr.get('value') for attr in x.get('attributes', [])}} if x else x
