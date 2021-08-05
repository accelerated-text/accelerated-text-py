# Python wrapper for Accelerated Text

## Installation
$ python -m pip install acctext
## Usage


```python
from acctext import AcceleratedText

at = AcceleratedText(host='http://127.0.0.1:3001')
```

Make sure Accelerated Text application is running.
Refer to [documentation](https://accelerated-text.readthedocs.io/en/latest/installation/) for launch instructions.


```python
at.health()
```




    {'health': 'Ok'}



### Interacting with Dictionary


```python
items = [{'key': 'house',
          'category': 'N',
          'forms': ['house', 'houses']},
         {'key': 'hill',
          'category': 'N',
          'forms': ['hill', 'hills']},
         {'key': 'on',
          'forms': ['on'],
          'category': 'Prep',
          'attributes': {'Operation': 'Syntax.on_Prep/Prep'}},
         {'key': 'the',
          'forms': ['the'],
          'category': 'Det',
          'attributes': {'Operation': 'Syntax.the_Det/Det'}}]

for item in items:
    at.create_dictionary_item(**item)
    
items = at.list_dictionary_items()
items
```




    [{'id': 'the_Det_Eng',
      'key': 'the',
      'forms': ['the'],
      'category': 'Det',
      'language': 'Eng',
      'attributes': {'Operation': 'Syntax.the_Det/Det'}},
     {'id': 'hill_N_Eng',
      'key': 'hill',
      'forms': ['hill', 'hills'],
      'category': 'N',
      'language': 'Eng',
      'attributes': {}},
     {'id': 'house_N_Eng',
      'key': 'house',
      'forms': ['house', 'houses'],
      'category': 'N',
      'language': 'Eng',
      'attributes': {}},
     {'id': 'on_Prep_Eng',
      'key': 'on',
      'forms': ['on'],
      'category': 'Prep',
      'language': 'Eng',
      'attributes': {'Operation': 'Syntax.on_Prep/Prep'}}]



### Working with Data

#### Upload a local file


```python
at.upload_data_file('example_data.csv')
```




    {'message': 'Succesfully uploaded file', 'id': 'example_data.csv'}



#### Create a data file from scratch


```python
at.create_data_file('example_data_2.csv', ['a', 'b'], [['1', '2'], ['3', '4']])
```




    {'id': 'example_data_2.csv'}



#### List available data files


```python
[x['id'] for x in at.list_data_files()]
```




    ['example_data.csv', 'example_data_2.csv']



#### Fetch data file


```python
at.get_data_file('example_data_2.csv')
```




    {'id': 'example_data_2.csv',
     'filename': 'example_data_2.csv',
     'header': ['a', 'b'],
     'rows': [['1', '2'], ['3', '4']]}



#### Delete data file


```python
at.delete_data_file('example_data_2.csv')
```




    {'message': 'Succesfully deleted file', 'id': 'example_data_2.csv'}



### Languages and Readers

#### Fetch existing language properties


```python
at.get_language('Eng')
```




    {'id': 'Eng', 'name': 'English', 'flag': '🇬🇧', 'default': True}



#### Add new language


```python
at.add_language('Ger', 'German')
```




    {'id': 'Ger', 'name': 'German', 'flag': '🇩🇪', 'default': False}



#### List available languages


```python
at.list_languages()
```




    [{'id': 'Eng', 'name': 'English', 'flag': '🇬🇧', 'default': True},
     {'id': 'Ger', 'name': 'German', 'flag': '🇩🇪', 'default': False}]



#### Create new reader type


```python
at.create_reader('Dc', 'Discount Customer', '(DC)')
```




    {'id': 'Dc', 'name': 'Discount Customer', 'flag': '(DC)', 'default': False}




```python
at.create_reader('Lc', 'Loyal Customer', '(LC)')
```




    {'id': 'Lc', 'name': 'Loyal Customer', 'flag': '(LC)', 'default': False}



#### List available readers


```python
at.list_readers()
```




    [{'id': 'Dc', 'name': 'Discount Customer', 'flag': '(DC)', 'default': False},
     {'id': 'Lc', 'name': 'Loyal Customer', 'flag': '(LC)', 'default': False}]



### Document plans

Open Accelerated Text document plan editor ([http://127.0.0.1:8080](http://127.0.0.1:8080) by default) and create a new document plan named **"House description"**. More detailed instructions can be found in [documentation](https://accelerated-text.readthedocs.io/en/latest/first-steps/).

![House description](https://raw.githubusercontent.com/tokenmill/accelerated-text-py/master/resources/house_description.png)


#### Fetch single document plan


```python
dp = at.get_document_plan(name='House description')
dp['documentPlan']
```




    {'type': 'Document-plan',
     'segments': [{'children': [{'modifier': {'name': 'size',
          'type': 'Cell-modifier',
          'srcId': 'B-D0i/`TL4@ja%{U!?2G',
          'child': {'name': 'color',
           'type': 'Cell-modifier',
           'srcId': '!2b?}PBIB?i]%*/(~?XM',
           'child': {'name': 'house',
            'type': 'Dictionary-item',
            'srcId': '+5JLY;_/2/zEOcZ._$,4',
            'kind': 'N',
            'itemId': 'house_N_Eng'}}},
         'type': 'Modifier',
         'srcId': '`62!swypAqp_jK_lr1Ow',
         'child': {'name': 'on',
          'type': 'Dictionary-item-modifier',
          'srcId': ']MNfAFBjxy,c?G55a04@',
          'kind': 'Prep',
          'child': {'name': 'the',
           'type': 'Dictionary-item-modifier',
           'srcId': '62%#$13DP}Gj8=n4NCI.',
           'kind': 'Det',
           'child': {'name': 'hill',
            'type': 'Dictionary-item',
            'srcId': 'Ol68tPXKblg(pUghVhb@',
            'kind': 'N',
            'itemId': 'hill_N_Eng'},
           'itemId': 'the_Det_Eng'},
          'itemId': 'on_Prep_Eng'}}],
       'type': 'Segment',
       'srcId': ']H[rfMhNu,^(wX6[%.+w'}],
     'srcId': 'Li$gv+b_9o-n$z^FnSl~'}



#### Delete document plan


```python
at.delete_document_plan(dp['id'])
```




    True



#### Restore document plan


```python
at.create_document_plan(**dp)['name']
```




    'House description'



#### List document plans


```python
[x['name'] for x in at.list_document_plans(kind='Document')]
```




    ['House description']



### Text generation


```python
result = at.generate('House description', data={"size": "small", "color": "red"})
result['variants']
```




    ['Small red house on the hill.']



#### Bulk generation


```python
results = at.generate_bulk('House description', data=[{"size": "small", "color": "red"}, 
                                                      {"size": "big", "color": "green"}])
[x['variants'] for x in results]
```




    [['Small red house on the hill.'], ['Big green house on the hill.']]



#### Fetch specific result


```python
at.get_result(result['resultId'])
```




    {'resultId': 'a364335f-5021-443d-9c77-fe40c296ecef',
     'offset': 0,
     'totalCount': 1,
     'ready': True,
     'updatedAt': 1628173135,
     'variants': ['Small red house on the hill.']}



### Working with state

#### Export


```python
at.export_state('state.zip')
```

#### Clear


```python
at.clear_state()
```

#### Restore


```python
at.restore_state('state.zip')
```
