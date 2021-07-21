create_dictionary_item = """mutation CreateDictionaryItem($id: ID, $name: String!, $partOfSpeech: PartOfSpeech, $key: String, $forms: [String], $language: Language, $sense: String, $definition: String, $attributes: [Attribute]) {
    createDictionaryItem(id: $id, name: $name, partOfSpeech: $partOfSpeech, key: $key, forms: $forms, language: $language, sense: $sense, definition: $definition, attributes: $attributes) {
        id
        name
        partOfSpeech
        language
        phrases {
            text
        }
        attributes {
            name
            value
        }
    }
}
"""

create_document_plan = """mutation createDocumentPlan($id: ID, $uid: ID!, $name: String!, $kind: String, $examples: [String], $blocklyXml: String!, $documentPlan: String!, $dataSampleId: ID, $dataSampleRow: Int) {
    createDocumentPlan(id: $id, uid: $uid, name: $name, kind: $kind, examples: $examples, blocklyXml: $blocklyXml, documentPlan: $documentPlan, dataSampleId: $dataSampleId, dataSampleRow: $dataSampleRow) {
        ...documentPlanFields
        __typename
    }
}

fragment documentPlanFields on DocumentPlan {
    id
    uid
    name
    kind
    examples
    blocklyXml
    documentPlan
    dataSampleId
    dataSampleRow
    createdAt
    updatedAt
    updateCount
    __typename
}
"""

delete_dictionary_item = """mutation DeleteDictionaryItem($id: ID!) {
    deleteDictionaryItem(id: $id)
}
"""

delete_document_plan = """mutation deleteDocumentPlan($id: ID!) {
    deleteDocumentPlan(id: $id)
}
"""

get_data_file = """query getDataFile($id: ID!, $recordOffset: Int, $recordLimit: Int) {
  getDataFile(id: $id, recordOffset: $recordOffset, recordLimit: $recordLimit) {
    id
    fileName
    fieldNames
    records {
      id
      fields {
        id
        fieldName
        value
      }
    }
    recordOffset
    recordLimit
    recordCount
  }
}
"""

create_data_file = """mutation createDataFile($id: ID, $filename: String, $content: String) {
  createDataFile(id: $id, filename: $filename, content: $content) {
    id
  }
}
"""

list_data_files = """query listDataFiles(
  $offset: Int
  $limit: Int
  $recordOffset: Int
  $recordLimit: Int
) {
  listDataFiles(
    offset: $offset
    limit: $limit
    recordOffset: $recordOffset
    recordLimit: $recordLimit
  ) {
    offset
    limit
    totalCount
    dataFiles {
      id
      fileName
      fieldNames
      records {
        id
        fields {
          id
          fieldName
          value
        }
      }
      recordOffset
      recordLimit
      recordCount
    }
  }
}
"""

dictionary = """query dictionary {
    dictionary {
        items {
            id
            name
            partOfSpeech
            language
            phrases {
                text
                }
            attributes {
                name
                value
                }
            }
        }
    }
}
"""

document_plan = """query documentPlan($id: ID, $name: String) {
  documentPlan(id: $id, name: $name) {
    id
    uid
    name
    kind
    examples
    blocklyXml
    documentPlan
  }
}
"""


document_plans = """query documentPlans($offset: Int!, $limit: Int!, $kind: String) {
    documentPlans(offset: $offset, limit: $limit, kind: $kind) {
        items {
            id
            uid
            name
            kind
            examples     
            blocklyXml
            documentPlan
        }
        offset
        limit
        totalCount
    }
}
"""

get_dictionary_item = """query dictionaryItem(
    $dictionaryItemId: ID!
) {
    dictionaryItem(
        id: $dictionaryItemId
    ) {
        id
        name
        partOfSpeech
        language
        phrases {
            text
        }
        attributes {
            name
            value
        }
    }
}
"""

reader_flag = """query readerFlag($id: ID!) {
  readerFlag(id: $id) {
    id
    name
    flag
    defaultUsage
  }
}
"""

create_reader_flag = """mutation createReaderFlag(
  $id: ID!
  $name: String!
  $flag: String!
  $defaultUsage: Usage!
) {
  createReaderFlag(
    id: $id
    name: $name
    flag: $flag
    defaultUsage: $defaultUsage
  ) {
    id
    name
    flag
    defaultUsage
  }
}
"""

delete_reader_flag = """mutation deleteReaderFlag($id: ID!) {
  deleteReaderFlag(id: $id)
}
"""

reader_flags = """query readerFlags {
  readerFlags {
    flags {
      id
      name
      flag
      defaultUsage
    }
  }
}
"""

language = """query language($id: Language!) {
  language(id: $id) {
    id
    name
    flag
    defaultUsage
  }
}
"""

add_language = """mutation addLanguage(
  $id: Language!
  $name: String!
  $flag: String
  $defaultUsage: Usage!
) {
  addLanguage(
    id: $id
    name: $name
    flag: $flag
    defaultUsage: $defaultUsage
  ) {
    id
    name
    flag
    defaultUsage
  }
}
"""

delete_language = """mutation deleteLanguage($id: Language!) {
  deleteLanguage(id: $id)
}
"""

languages = """query languages {
  languages {
    flags {
      id
      name
      flag
      defaultUsage
    }
  }
}
"""
