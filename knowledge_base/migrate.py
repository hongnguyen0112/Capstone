from typedb.client import TypeDB, SessionType, TransactionType
import csv


def build_product_graph(inputs):
    with TypeDB.core_client("localhost:1729") as client:
        with client.session("local", SessionType.DATA) as session:
            for input in inputs:
                print("Loading from [" + input["data_path"] + "] into TypeDB ...")
                load_data_into_grakn(input, session)


def load_data_into_grakn(input, session):
    items = parse_data_to_dictionaries(input)

    for item in items:
        with session.transaction(TransactionType.WRITE) as transaction:
            typeql_insert_query = input["template"](item)
            print("Executing TypeQL Query: " + typeql_insert_query)
            transaction.query().insert(typeql_insert_query)
            transaction.commit()

    print("\nInserted " + str(len(items)) + " items from [ " + input["data_path"] + "] into TypeDB.\n")


def product_template(product_info):
    return 'insert $Product_info isa Product_info, has Product "' + product_info["Product"] + '";'


def tcss_template(tcss_info):
    return 'insert $TCSS_info isa TCSS_info, has TCSS "' + tcss_info["TCSS"] + '";'


def at_site_template(at_site_info):
    return 'insert $AT_Site_info isa AT_Site_info, has AT_Site "' + at_site_info["AT_Site"] + '";'


def cycle_template(cycle_info):
    return 'insert $Cycle_info isa Cycle_info, has Cycle "' + cycle_info["Cycle"] + '";'


def phase_template(phase_info):
    return 'insert $Phase_info isa Phase_info, has Phase "' + phase_info["Phase"] + '";'


def testerplatform_template(testerplatform_info):
    return 'insert $Tester_Platform_info isa Tester_Platform_info, has Tester_Platform "' + \
           testerplatform_info["Tester_Platform"] + '";'


def segment_template(segment_info):
    return 'insert $Segment_info isa Segment_info, has Segment "' + segment_info["Segment"] + '";'


def division_template(division_info):
    return 'insert $Division_info isa Division_info, has Division "' + division_info["Division"] + '";'


def package_tech_template(package_tech_info):
    return 'insert $Package_Tech_info isa Package_Tech_info, has Package_Tech "' + package_tech_info[
        "Package_Tech"] + '";'


def chip_attach_template(chip_attach_info):
    return 'insert $Chip_Attach_info isa Chip_Attach_info, has Chip_Attach "' + chip_attach_info[
        "Chip_Attach"] + '";'


def product_details_template(product_details):
    typeql_insert_query = 'match $Product_info isa Product_info,' \
                          ' has Product "' + product_details["Product"] + '";'
    typeql_insert_query += ' $Segment_info isa Segment_info, has Segment "' + product_details["Segment"] + '";'
    typeql_insert_query += ' $TCSS_info isa TCSS_info, has TCSS "' + product_details["TCSS"] + '";'
    typeql_insert_query += ' $Package_Tech_info isa Package_Tech_info,' \
                           ' has Package_Tech "' + product_details["Package_Tech"] + '";'
    typeql_insert_query += ' $Chip_Attach_info isa Chip_Attach_info,' \
                           ' has Chip_Attach "' + product_details["Chip_Attach"] + '";'
    typeql_insert_query += ' $Tester_Platform_info isa Tester_Platform_info,' \
                           ' has Tester_Platform "' + product_details["Tester_Platform"] + '";'
    typeql_insert_query += ' $AT_Site_info isa AT_Site_info, has AT_Site "' + product_details["AT_Site"] + '";'
    typeql_insert_query += ' $Division_info isa Division_info, has Division "' + product_details["Division"] + '";'
    typeql_insert_query += " insert" \
                           " (Product: $Product_info," \
                           " Segment: $Segment_info," \
                           " TCSS: $TCSS_info," \
                           " Package_Tech: $Package_Tech_info," \
                           " Chip_Attach: $Chip_Attach_info," \
                           " Tester_Platform: $Tester_Platform_info," \
                           " AT_Site: $AT_Site_info," \
                           " Division: $Division_info) isa product_details;"
    return typeql_insert_query


def production_log_template(production_log):
    typeql_insert_query = 'match $Product_info isa Product_info, has Product "' + production_log["Product"] + '";'
    typeql_insert_query += ' $Cycle_info isa Cycle_info, has Cycle "' + production_log["Cycle"] + '";'
    typeql_insert_query += ' $Phase_info isa Phase_info, has Phase "' + production_log["Phase"] + '";'
    typeql_insert_query += " insert (Product: $Product_info," \
                           " Phase: $Phase_info," \
                           " Cycle: $Cycle_info) isa production_log," \
                           " has Comment '" + production_log["Comment"] + "'," +  \
                           " has WW '" + production_log["WW"] + "';"

    return typeql_insert_query


def product_cycle_template(product_cycle):
    typeql_insert_query = 'match $Product_info isa Product_info, has Product "' + product_cycle["Product"] + '";'
    typeql_insert_query += ' $Cycle_info isa Cycle_info, has Cycle "' + product_cycle["Cycle"] + '";'
    typeql_insert_query += " insert (Product: $Product_info, Cycle: $Cycle_info) isa product_cycle;"
    return typeql_insert_query


def mention_mapping_template(mapping):
    typeql_insert_query = 'insert $mapping isa mention_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    typeql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return typeql_insert_query


def attribute_mapping_template(mapping):
    typeql_insert_query = 'insert $mapping isa attribute_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    typeql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '"'
    typeql_insert_query += ', has object_type "' + mapping["object_type"] + '";'
    return typeql_insert_query


def object_type_mapping_template(mapping):
    typeql_insert_query = 'insert $mapping isa object_type_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    typeql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return typeql_insert_query


def parse_data_to_dictionaries(input):
    items = []
    with open(input["data_path"] + ".csv") as data:
        for row in csv.DictReader(data, skipinitialspace=True):
            item = {key: value for key, value in row.items()}
            items.append(item)
    return items


inputs = [
    {
        "data_path": "./data/product",
        "template": product_template
    },
    {
        "data_path": "./data/tcss",
        "template": tcss_template
    },
    {
        "data_path": "./data/at_site",
        "template": at_site_template
    },
    {
        "data_path": "./data/cycle",
        "template": cycle_template
    },
    {
        "data_path": "./data/phase",
        "template": phase_template
    },
    {
        "data_path": "./data/testerplatform",
        "template": testerplatform_template
    },
    {
        "data_path": "./data/division",
        "template": division_template
    },
    {
        "data_path": "./data/segment",
        "template": segment_template
    },
    {
        "data_path": "./data/package_tech",
        "template": package_tech_template
    },
    {
        "data_path": "./data/chip_attach",
        "template": chip_attach_template
    },
    {
        "data_path": "./data/product_details",
        "template": product_details_template
    },
    {
        "data_path": "./data/production_log",
        "template": production_log_template
    },
    {
        "data_path": "./data/product_cycle",
        "template": product_cycle_template
    },
    {
        "data_path": "./data/attribute_mapping",
        "template": attribute_mapping_template
    },
    {
        "data_path": "./data/mention_mapping",
        "template": mention_mapping_template
    },
    {
        "data_path": "./data/object_type_mapping",
        "template": object_type_mapping_template
    }
]

build_product_graph(inputs)

print("Migration complete.")

# exmaple of entity template
# def call_template(call):
#     typeql_insert_query = 'match $product, owns Product_RMIT "' + call["Product_RMIT"] + '";'
#     typeql_insert_query += 'match $product, owns Segment "' + call["Segment"] + '";'
#     typeql_insert_query += 'match $product, owns AT_Site "' + call["AT_Site"] + '";'
#     typeql_insert_query += 'match $product, owns Division "' + call["Division"] + '";'
#     typeql_insert_query += 'match $product, owns Package_Tech "' + call["Package_Tech"] + '";'
#     typeql_insert_query += 'match $product, owns Chip_Attach "' + call["Chip_Attach"] + '";'
#     typeql_insert_query += 'match $product, owns Tester_Platform "' + call["Tester_Platform"] + '";'
#     typeql_insert_query += 'match $product, owns cycle "' + call["cycle"] + '";'
#     typeql_insert_query += 'match $product, owns Phase "' + call["Phase"] + '";'
#     typeql_insert_query += 'match $product, owns WW "' + call["WW"] + '";'
#     typeql_insert_query += 'match $product, owns comment "' + call["comment"] + '";'
#     return typeql_insert_query


# example of relation template
# def include_phase_template(include_phase):
#     typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_phase["Product_RMIT"] + '";'
#     typeql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_phase["Phase"] + '";'
#     typeql_insert_query += " insert (product: $product, phase: $phase_info) isa include_phase;"
#     return typeql_insert_query
