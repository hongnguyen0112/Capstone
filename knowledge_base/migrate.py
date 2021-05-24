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
    graql_insert_query += ', has Tester_Platform "' + product["Tester_Platform"] + '";'
    return graql_insert_query


def cycle_template(cycle_info):
    graql_insert_query = 'insert $cycle_info isa cycle_info, has cycle "' + cycle_info["cycle"] + '";'
    return graql_insert_query


def phase_template(phase_info):
    graql_insert_query = 'insert $phase_info isa phase_info, has Phase "' + phase_info["Phase"] + '";'
    return graql_insert_query


def comment_template(comment_info):
    graql_insert_query = 'insert $comment_info isa comment_info, has WW "' + comment_info["WW"] + '"'
    graql_insert_query += ', has comment "' + comment_info["comment"] + '";'
    return graql_insert_query


def include_cycle_template(include_cycle):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_cycle["Product_RMIT"] + '";'
    graql_insert_query += ' $cycle_info isa cycle_info, has cycle "' + include_cycle["cycle"] + '";'
    graql_insert_query += " insert (product: $product, cycle: $cycle_info) isa include_cycle;"
    return graql_insert_query


def include_comment_template(include_comment):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_comment["Product_RMIT"] + '";'
    graql_insert_query += ' $cycle_info isa cycle_info, has cycle "' + include_comment["cycle"] + '";'
    graql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_comment["Phase"] + '";'
    graql_insert_query += ' $comment_info isa comment_info, has WW "' + include_comment["WW"] + '"'
    graql_insert_query += ', has comment "' + include_comment["comment"] + '";'
    graql_insert_query += " insert (product: $product, cycle: $cycle_info, phase: $phase_info, comment: $comment_info) isa include_comment;"
    return graql_insert_query


def include_phase_template(include_phase):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_phase["Product_RMIT"] + '";'
    graql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_phase["Phase"] + '";'
    graql_insert_query += " insert (product: $product, phase: $phase_info) isa include_phase;"
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


# exmaple of entity template 
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


# example of relation template
# def include_phase_template(include_phase):
#     graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_phase["Product_RMIT"] + '";'
#     graql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_phase["Phase"] + '";'
#     graql_insert_query += " insert (product: $product, phase: $phase_info) isa include_phase;"
#     return graql_insert_query


def build_product_graph(inputs):
    with Grakn.core_client("localhost:1729") as client:
        with client.session("product", SessionType.DATA) as session:
            for input in inputs:
                print("Loading from [" + input["data_path"] + "] into Grakn ...")
                load_data_into_grakn(input, session)

inputs = [
    {
        "data_path": "product",
        "template": product_template
    },
    {
        "data_path": "cycle",
        "template": cycle_template
    },
    {
        "data_path": "Phase",
        "template": phase_template
    },
    {
        "data_path": "comment",
        "template": comment_template
    },
    {
        "data_path": "include_comment",
        "template": include_comment_template
    },
    {
        "data_path": "include_cycle",
        "template": include_cycle_template
    },
    {
        "data_path": "include_phase",
        "template": include_phase_template
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