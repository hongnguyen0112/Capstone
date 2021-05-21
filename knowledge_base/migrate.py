from grakn.client import Grakn, SessionType, TransactionType
import csv

def parse_data_to_dictionaries(input):
    items = []
    with open(input["data_path"] + ".csv") as data:
        for row in csv.DictReader(data, skipinitialspace = True):
            item = { key: value for key, value in row.items() }
            items.append(item)
    return items


def load_data_into_grakn(input, session):
    items = parse_data_to_dictionaries(input)

    for item in items:
        with session.transaction(TransactionType.WRITE) as transaction:
            graql_insert_query = input["template"](item)
            print("Executing Graql Query: " + graql_insert_query)
            transaction.query().insert(graql_insert_query)
            transaction.commit()

    print("\nInserted " + str(len(items)) + " items from [ " + input["data_path"] + "] into Grakn.\n")


def product_template(product):
    graql_insert_query = 'insert $product isa product, has Product_RMIT "' + product["Product_RMIT"] + '"'
    graql_insert_query += ', has Segment "' + product["Segment"] + '"'
    graql_insert_query += ', has AT_Site "' + product["AT_Site"] + '"'
    graql_insert_query += ', has Division "' + product["Division"] + '"'
    graql_insert_query += ', has Package_Tech "' + product["Package_Tech"] + '"'
    graql_insert_query += ', has Chip_Attach "' + product["Chip_Attach"] + '"'
    graql_insert_query += ', has Tester_Platform "' + product["Tester_Platform"] + '"'
    graql_insert_query += ', has cycle "' + product["cycle"] + '"'
    graql_insert_query += ', has Phase "' + product["Phase"] + '"'
    graql_insert_query += ', has WW "' + product["WW"] + '"'
    graql_insert_query += ', has comment "' + product["comment"] + '";'
    return graql_insert_query

def mention_mapping_template(mapping):
    graql_insert_query = 'insert $mapping isa mention_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    graql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return graql_insert_query


def attribute_mapping_template(mapping):
    graql_insert_query = 'insert $mapping isa attribute_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    graql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return graql_insert_query


def object_type_mapping_template(mapping):
    graql_insert_query = 'insert $mapping isa object_type_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    graql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return graql_insert_query





# def call_template(call):
#     graql_insert_query = 'match $product, owns Product_RMIT "' + call["Product_RMIT"] + '";'
#     graql_insert_query += 'match $product, owns Segment "' + call["Segment"] + '";'
#     graql_insert_query += 'match $product, owns AT_Site "' + call["AT_Site"] + '";'
#     graql_insert_query += 'match $product, owns Division "' + call["Division"] + '";'
#     graql_insert_query += 'match $product, owns Package_Tech "' + call["Package_Tech"] + '";'
#     graql_insert_query += 'match $product, owns Chip_Attach "' + call["Chip_Attach"] + '";'
#     graql_insert_query += 'match $product, owns Tester_Platform "' + call["Tester_Platform"] + '";'
#     graql_insert_query += 'match $product, owns cycle "' + call["cycle"] + '";'
#     graql_insert_query += 'match $product, owns Phase "' + call["Phase"] + '";'
#     graql_insert_query += 'match $product, owns WW "' + call["WW"] + '";'
#     graql_insert_query += 'match $product, owns comment "' + call["comment"] + '";'
#     return graql_insert_query


def build_product_graph(inputs):
    with Grakn.core_client("localhost:1729") as client:
        with client.session("capstone", SessionType.DATA) as session:
            for input in inputs:
                print("Loading from [" + input["data_path"] + "] into Grakn ...")
                load_data_into_grakn(input, session)

inputs = [
    {
        "data_path": "product",
        "template": product_template
    },
    {
        "data_path": "attribute_mapping",
        "template": attribute_mapping_template
    },
    {
        "data_path": "mention_mapping",
        "template": mention_mapping_template
    },
    {
        "data_path": "object_type_mapping",
        "template": object_type_mapping_template
    }
]

build_product_graph(inputs)