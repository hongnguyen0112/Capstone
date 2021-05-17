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

def product_template(capstone):
    graql_insert_query = 'insert $product isa product, has Product_RMIT "' + capstone["Product_RMIT"] + '"'
    graql_insert_query += ', has Product_RMIT "' + capstone["Product_RMIT"] + '"'
    graql_insert_query += ', has Segment "' + capstone["Segment"] + '"'
    graql_insert_query += ', has AT_Site "' + capstone["AT_Site"] + '"'
    graql_insert_query += ', has Division "' + capstone["Division"] + '"'
    graql_insert_query += ', has Package_Tech "' + capstone["Package_Tech"] + '"'
    graql_insert_query += ', has Chip_Attach "' + capstone["Chip_Attach"] + '"'
    graql_insert_query += ', has Tester_Platform "' + capstone["Tester_Platform"] + '"'
    graql_insert_query += ', has cycle "' + capstone["cycle"] + '"'
    graql_insert_query += ', has Phase "' + capstone["Phase"] + '"'
    graql_insert_query += ', has WW "' + capstone["WW"] + '"'
    graql_insert_query += ', has comment "' + capstone["comment"] + '";'
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
    }
]

build_product_graph(inputs)