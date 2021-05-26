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
    graql_insert_query += ', has AT_Site "' + product["AT_Site"] + '";'
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

def testerplatform_template(testerplatform_info):
    graql_insert_query = 'insert $testerplatform_info isa testerplatform_info, has Tester_Platform "' + testerplatform_info["Tester_Platform"] + '";'
    return graql_insert_query

def segment_template(segment_info):
    graql_insert_query = 'insert $segment_info isa segment_info, has Segment "' + segment_info["Segment"] + '";'
    return graql_insert_query

def division_template(division_info):
    graql_insert_query = 'insert $division_info isa division_info, has Division "' + division_info["Division"] + '";'
    return graql_insert_query

def package_tech_template(package_tech_info):
    graql_insert_query = 'insert $package_tech_info isa package_tech_info, has Package_Tech "' + package_tech_info["Package_Tech"] + '";'
    return graql_insert_query

def chip_attach_template(chip_attach_info):
    graql_insert_query = 'insert $chip_attach_info isa chip_attach_info, has Chip_Attach "' + chip_attach_info["Chip_Attach"] + '";'
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


def include_testerplatform_template(include_testerplatform):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_testerplatform["Product_RMIT"] + '";'
    graql_insert_query += ' $testerplatform_info isa testerplatform_info, has Tester_Platform "' + include_testerplatform["Tester_Platform"] + '";'
    graql_insert_query += " insert (product: $product, Tester_Platform: $testerplatform_info) isa include_testerplatform;"
    return graql_insert_query

def include_segment_template(include_segment):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_segment["Product_RMIT"] + '";'
    graql_insert_query += ' $segment_info isa segment_info, has Segment "' + include_segment["Segment"] + '";'
    graql_insert_query += " insert (product: $product, Segment: $segment_info) isa include_segment;"
    return graql_insert_query

def include_division_template(include_division):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_division["Product_RMIT"] + '";'
    graql_insert_query += ' $division_info isa division_info, has Division "' + include_division["Division"] + '";'
    graql_insert_query += " insert (product: $product, Division: $division_info) isa include_division;"
    return graql_insert_query

def include_package_tech_template(include_package_tech):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_package_tech["Product_RMIT"] + '";'
    graql_insert_query += ' $package_tech_info isa package_tech_info, has Package_Tech "' + include_package_tech["Package_Tech"] + '";'
    graql_insert_query += " insert (product: $product, Package_Tech: $package_tech_info) isa include_package_tech;"
    return graql_insert_query

def include_chip_attach_template(include_chip_attach):
    graql_insert_query = 'match $product isa product, has Product_RMIT "' + include_chip_attach["Product_RMIT"] + '";'
    graql_insert_query += ' $chip_attach_info isa chip_attach_info, has Chip_Attach "' + include_chip_attach["Chip_Attach"] + '";'
    graql_insert_query += " insert (product: $product, Chip_Attach: $chip_attach_info) isa include_chip_attach;"
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
        "data_path": "testerplatform",
        "template": testerplatform_template
    },
    {
        "data_path": "division",
        "template": division_template
    },
    {
        "data_path": "segment",
        "template": segment_template
    },
    {
        "data_path": "package_tech",
        "template": package_tech_template
    },
    {
        "data_path": "chip_attach",
        "template": chip_attach_template
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
        "data_path": "include_testerplatform",
        "template": include_testerplatform_template
    },
    {
        "data_path": "include_segment",
        "template": include_segment_template
    },
    {
        "data_path": "include_division",
        "template": include_division_template
    },
    {
        "data_path": "include_package_tech",
        "template": include_package_tech_template
    },
    {
        "data_path": "include_chip_attach",
        "template": include_chip_attach_template
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