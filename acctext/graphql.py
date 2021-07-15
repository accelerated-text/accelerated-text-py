create_dictionary_item = """mutation CreateDictionaryItem($id: ID, $name: String!, $partOfSpeech: PartOfSpeech, $key: String, $forms: [String], $language: Language, $sense: String, $definition: String, $attributes: [Attribute]) {
    createDictionaryItem(id: $id, name: $name, partOfSpeech: $partOfSpeech, key: $key, forms: $forms, language: $language, sense: $sense, definition: $definition, attributes: $attributes) {
        id
        name
        partOfSpeech
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

dictionary = """query dictionary {
    dictionary {
        items {
            id
            name
            partOfSpeech
            phrases {
                id
                text
                defaultUsage
                readerFlagUsage {
                    id
                    usage
                    flag {
                        id
                        name
                    }
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
