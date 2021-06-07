from typedb.client import TypeDB, SessionType, TransactionType
import csv


def build_product_graph(inputs):
    with TypeDB.core_client("localhost:1729") as client:
        with client.session("product", SessionType.DATA) as session:
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


def product_template(product):
    return 'insert $product isa product, has Product_RMIT "' + product["Product_RMIT"] + '";'


def tcss_template(tcss_info):
    return 'insert $tcss_info isa tcss_info, has TCSS "' + tcss_info["TCSS"] + '";'


def at_site_template(at_site_info):
    return 'insert $at_site_info isa at_site_info, has AT_Site "' + at_site_info["AT_Site"] + '";'


def cycle_template(cycle_info):
    return 'insert $cycle_info isa cycle_info, has cycle "' + cycle_info["cycle"] + '";'


def phase_template(phase_info):
    return 'insert $phase_info isa phase_info, has Phase "' + phase_info["Phase"] + '";'


def comment_template(comment_info):
    typeql_insert_query = 'insert $comment_info isa comment_info, has WW "' + comment_info["WW"] + '"'
    typeql_insert_query += ', has comment "' + comment_info["comment"] + '";'
    return typeql_insert_query


def testerplatform_template(testerplatform_info):
    return 'insert $testerplatform_info isa testerplatform_info, has Tester_Platform "' + \
           testerplatform_info["Tester_Platform"] + '";'


def segment_template(segment_info):
    return 'insert $segment_info isa segment_info, has Segment "' + segment_info["Segment"] + '";'


def division_template(division_info):
    return 'insert $division_info isa division_info, has Division "' + division_info["Division"] + '";'


def package_tech_template(package_tech_info):
    return 'insert $package_tech_info isa package_tech_info, has Package_Tech "' + package_tech_info[
        "Package_Tech"] + '";'


def chip_attach_template(chip_attach_info):
    return 'insert $chip_attach_info isa chip_attach_info, has Chip_Attach "' + chip_attach_info[
        "Chip_Attach"] + '";'


def include_tcss_template(include_tcss):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_tcss["Product_RMIT"] + '";'
    typeql_insert_query += ' $tcss_info isa tcss_info, has TCSS "' + include_tcss["TCSS"] + '";'
    typeql_insert_query += " insert (product: $product, tcss: $tcss_info) isa include_tcss;"
    return typeql_insert_query


def include_at_site_template(include_at_site):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_at_site["Product_RMIT"] + '";'
    typeql_insert_query += ' $at_site_info isa at_site_info, has AT_Site "' + include_at_site["AT_Site"] + '";'
    typeql_insert_query += " insert (product: $product, at_site: $at_site_info) isa include_at_site;"
    return typeql_insert_query


def include_cycle_template(include_cycle):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_cycle["Product_RMIT"] + '";'
    typeql_insert_query += ' $cycle_info isa cycle_info, has cycle "' + include_cycle["cycle"] + '";'
    typeql_insert_query += " insert (product: $product, cycle: $cycle_info) isa include_cycle;"
    return typeql_insert_query


def include_comment_template(include_comment):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_comment["Product_RMIT"] + '";'
    typeql_insert_query += ' $cycle_info isa cycle_info, has cycle "' + include_comment["cycle"] + '";'
    typeql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_comment["Phase"] + '";'
    typeql_insert_query += ' $comment_info isa comment_info, has WW "' + include_comment["WW"] + '"'
    typeql_insert_query += ', has comment "' + include_comment["comment"] + '";'
    typeql_insert_query += " insert (product: $product, cycle: $cycle_info, " \
                           "phase: $phase_info, comment: $comment_info) isa include_comment;"
    return typeql_insert_query


def include_phase_template(include_phase):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_phase["Product_RMIT"] + '";'
    typeql_insert_query += ' $phase_info isa phase_info, has Phase "' + include_phase["Phase"] + '";'
    typeql_insert_query += " insert (product: $product, phase: $phase_info) isa include_phase;"
    return typeql_insert_query


def include_testerplatform_template(include_testerplatform):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_testerplatform[
        "Product_RMIT"] + '";'
    typeql_insert_query += ' $testerplatform_info isa testerplatform_info, has Tester_Platform "' + \
                           include_testerplatform["Tester_Platform"] + '";'
    typeql_insert_query += " insert (product: $product, " \
                           "Tester_Platform: $testerplatform_info) isa include_testerplatform;"
    return typeql_insert_query


def include_segment_template(include_segment):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_segment["Product_RMIT"] + '";'
    typeql_insert_query += ' $segment_info isa segment_info, has Segment "' + include_segment["Segment"] + '";'
    typeql_insert_query += " insert (product: $product, Segment: $segment_info) isa include_segment;"
    return typeql_insert_query


def include_division_template(include_division):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_division["Product_RMIT"] + '";'
    typeql_insert_query += ' $division_info isa division_info, has Division "' + include_division["Division"] + '";'
    typeql_insert_query += " insert (product: $product, Division: $division_info) isa include_division;"
    return typeql_insert_query


def include_package_tech_template(include_package_tech):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_package_tech["Product_RMIT"] + '";'
    typeql_insert_query += ' $package_tech_info isa package_tech_info, has Package_Tech "' + include_package_tech[
        "Package_Tech"] + '";'
    typeql_insert_query += " insert (product: $product, Package_Tech: $package_tech_info) isa include_package_tech;"
    return typeql_insert_query


def include_chip_attach_template(include_chip_attach):
    typeql_insert_query = 'match $product isa product, has Product_RMIT "' + include_chip_attach["Product_RMIT"] + '";'
    typeql_insert_query += ' $chip_attach_info isa chip_attach_info, has Chip_Attach "' + include_chip_attach[
        "Chip_Attach"] + '";'
    typeql_insert_query += " insert (product: $product, Chip_Attach: $chip_attach_info) isa include_chip_attach;"
    return typeql_insert_query


def mention_mapping_template(mapping):
    typeql_insert_query = 'insert $mapping isa mention_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    typeql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
    return typeql_insert_query


def attribute_mapping_template(mapping):
    typeql_insert_query = 'insert $mapping isa attribute_mapping, has mapping_key "' + mapping["mapping_key"] + '"'
    typeql_insert_query += ', has mapping_value "' + mapping["mapping_value"] + '";'
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
        "data_path": "./data/Phase",
        "template": phase_template
    },
    {
        "data_path": "./data/comment",
        "template": comment_template
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
        "data_path": "./data/include_comment",
        "template": include_comment_template
    },
    {
        "data_path": "./data/include_tcss",
        "template": include_tcss_template
    },
    {
        "data_path": "./data/include_at_site",
        "template": include_at_site_template
    },
    {
        "data_path": "./data/include_cycle",
        "template": include_cycle_template
    },
    {
        "data_path": "./data/include_phase",
        "template": include_phase_template
    },
    {
        "data_path": "./data/include_testerplatform",
        "template": include_testerplatform_template
    },
    {
        "data_path": "./data/include_segment",
        "template": include_segment_template
    },
    {
        "data_path": "./data/include_division",
        "template": include_division_template
    },
    {
        "data_path": "./data/include_package_tech",
        "template": include_package_tech_template
    },
    {
        "data_path": "./data/include_chip_attach",
        "template": include_chip_attach_template
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
