# -*- coding: utf-8 -*-
from typing import Text, Dict, Any, List, Union
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict

from schema import schema
from graph_database import GraphDatabase


def resolve_mention(tracker: Tracker) -> Text:
    """
    Resolves a mention of an entity, such as first, to the actual entity.
    If multiple entities are listed during the conversation, the entities
    are stored in the slot 'listed_items' as a list. We resolve the mention,
    such as first, to the list index and retrieve the actual entity.
    :param tracker: tracker
    :return: name of the actually entity
    """
    graph_database = GraphDatabase()
    mention = tracker.get_slot("mention")
    listed_items = tracker.get_slot("listed_items")

    if mention is not None and listed_items is not None:
        idx = int(graph_database.map("mention_mapping", mention))

        if type(idx) is int and idx < len(listed_items):
            return listed_items[idx]


def get_object_type(tracker: Tracker) -> Text:
    """
    Get the object_type synonym mentioned by the user. As the user may speak of an
    entity type in plural, we need to map the mentioned synonym to the
    object_type used in the knowledge base.
    :param tracker: tracker
    :return: object_type (same type as used in the knowledge base)
    """
    graph_database = GraphDatabase()
    object_type = tracker.get_slot("object_type")
    print("- Inputed object_type: ", object_type)
    return graph_database.map("object_type_mapping", object_type)


def get_attribute(tracker: Tracker) -> Text:
    """
    Get the attribute mentioned by the user. As the user may use a synonym for
    an attribute, we need to map the mentioned attribute to the
    attribute name used in the knowledge base.
    :param tracker: tracker
    :return: attribute (same type as used in the knowledge base)
    """
    print("\n- Get target attribute")
    graph_database = GraphDatabase()
    attribute = tracker.get_slot("attribute")
    return graph_database.map("attribute_mapping", attribute)


def get_object_type_of_attribute(attribute) -> Text:
    graph_database = GraphDatabase()
    return graph_database.get_obj_of_attribute(attribute)


def get_entity_name(tracker: Tracker, object_type: Text):
    """
    Get the name of the entity the user referred to. Either the NER detected the
    entity and stored its name in the corresponding slot or the user referred to
    the entity by an ordinal number, such as first or last, or the user refers to
    an entity by its attributes.
    :param tracker: Tracker
    :param object_type: the object_type
    :return: the name of the actual entity (value of key attribute in the knowledge base)
    """
    print("\n- Get entity name")
    # mention = tracker.get_slot("mention")

    # if mention is not None:
    #     return resolve_mention(tracker)

    # entity_name = tracker.get_slot(object_type)
    # if entity_name:
    #     return entity_name

    listed_items = tracker.get_slot("listed_items")
    attributes = get_attributes_of_entity(object_type, tracker)
    relates = get_relates_of_relations(object_type, tracker)

    if relates:
        entity_name = relates[0]['value']
        print("\t- Entity name: ", entity_name)
        return entity_name

    if listed_items and attributes:
        graph_database = GraphDatabase()

        for entity in listed_items:
            key_attr = schema[object_type]["key"]
            result = graph_database.validate_entity(
                object_type, entity, key_attr, attributes
            )

            if result is not None:
                return to_str(result, key_attr)

    return None


def get_attributes_of_entity(object_type, tracker):
    # check what attributes the NER found for object type
    attributes = []
    if object_type in schema:
        for attr in schema[object_type]["attributes"]:
            attr_val = tracker.get_slot(attr.replace("-", "_"))
            if attr_val is not None:
                attributes.append({"key": attr, "value": attr_val})

    return attributes


def get_relates_of_relations(object_type, tracker):
    # Check available relates of a relation
    relates = []
    if object_type in schema:
        for relate in schema[object_type]["relates"]:
            relate_val = tracker.get_slot(relate.replace("-", "_"))
            if relate_val is not None:
                relates.append({"key": relate, "value": relate_val})

    return relates


def reset_attribute_slots(slots, object_type, tracker):
    # check what attributes the NER found for entity type
    if object_type in schema:

        for attr in schema[object_type]["attributes"]:
            attr = attr.replace("-", "_")
            attr_val = tracker.get_slot(attr)

            if attr_val is not None:
                slots.append(SlotSet(attr, None))
    print("\nreset_attribute_slots: ", slots)
    return slots


def to_str(entity: Dict[Text, Any], entity_keys: Union[Text, List[Text]]) -> Text:
    """
    Converts an entity to a string by concatenating the values of the provided
    entity keys.
    :param entity: the entity with all its attributes
    :param entity_keys: the name of the key attributes
    :return: a string that represents the entity
    """
    if isinstance(entity_keys, str):
        entity_keys = [entity_keys]
    v_list = []
    for key in entity_keys:
        _e = entity
        for k in key.split("."):
            _e = _e[k]
        if _e not in v_list:
            v_list.append(str(_e))
    return ", ".join(v_list)


class ActionQueryEntities(Action):
    """
    Action for listing entities.
    The entities might be filtered by specific attributes.
    """

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher, tracker, domain):
        print("\n* Action: Query Entities.\n")
        graph_database = GraphDatabase()

        # need to know the object_type we are looking for
        object_type = get_object_type(tracker)

        # utter rephrase if found no object_type recognised
        if object_type is None:
            dispatcher.utter_message(response="utter_rephrase")
            return []

        # check what attributes the NER found for entity type
        attributes = get_attributes_of_entity(object_type, tracker)

        # query knowledge base

        print("\n- Classify object_type")
        if "relates" in schema[object_type]:
            print("\t- Type: Relation")
            relates = get_relates_of_relations(object_type, tracker)
            print("\n- Query", object_type, "entities.")
            entities = graph_database.get_relations(object_type, relates, attributes)
        else:
            print("\t- Type: Entity")
            print("\n- Query", object_type, "entities.")
            entities = graph_database.get_entities(object_type, attributes)

        if entities:
            print("\nFound the follwing:")
            for entity in entities:
                print(entity, "\n")

        # utter message if no instance is found with the object_type
        if not entities:
            print("\nNo entity satisfied criteria")
            dispatcher.utter_message(
                "I could not find anything satisfying to your query... Rephrase maybe?"
            )
            return []

        """
        Utter response and list all found instances 
        """
        # use the 'representation' attributes to print an entity
        entity_representation = schema[object_type]["representation"]

        dispatcher.utter_message(
            "I have found the following: "
        )

        sorted_entities = sorted([to_str(e, entity_representation) for e in entities])
        for i, e in enumerate(sorted_entities):
            dispatcher.utter_message(f"{i + 1}: {e}")

        # set slots
        # set the entities slot in order to resolve references to one of the found
        # entities later on
        entity_key = schema[object_type]["key"]

        # Number items in result list
        slots = [
            SlotSet("object_type", object_type),
            SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        ]

        # if only one entity was found, that the slot of that entity type to the found entity
        if len(entities) == 1:
            slots.append(SlotSet(object_type, to_str(entities[0], entity_key)))

        reset_attribute_slots(slots, object_type, tracker)
        print("\nEntity query complete.\n")

        return slots


class ActionQueryAttribute(Action):
    """
    Action for querying a specific attribute of an entity.
    """
    def name(self):
        return "action_query_attribute"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()
        print("\n* Action Query Attribute")

        # Get target attribute of interest
        target = get_attribute(tracker)

        # get object_type of target entity
        print("- Get object_type")
        object_type = get_object_type_of_attribute(target)

        # utter rephrase if no object_type found
        if object_type is None:
            dispatcher.utter_message(response="utter_rephrase")
            return []

        # get name of entity and attribute of interest
        name = get_entity_name(tracker, object_type)

        # utter rephrase if no name or attribute recognised
        if name is None or target is None:
            dispatcher.utter_message(response="utter_rephrase")
            slots = [SlotSet("mention", None)]
            reset_attribute_slots(slots, object_type, tracker)
            return slots

        relates = get_relates_of_relations(object_type, tracker)
        attributes = get_attributes_of_entity(object_type, tracker)
        target_attribute = ""
        target_relate = ""

        if object_type in schema:
            if target in schema[object_type]["relates"]:
                target_relate = target
            elif target in schema[object_type]["attributes"]:
                target_attribute = target

        print("\n- Object_type: ", object_type)
        print("- Provided attribute: ", attributes)
        print("- Provided relates: ", relates)
        print("- Target attribute: ", target_attribute)
        print("- Target relates: ", target_relate)

        # query knowledge base
        print("\n- Query attribute:")
        value = graph_database.get_attribute_of(
            object_type, target_attribute, target_relate, attributes, relates,
        )

        # utter response
        if value is not None and len(value) == 1:
            dispatcher.utter_message(
                f"Found {name} has {target}: {value[0]}."
            )
        else:
            dispatcher.utter_message(
                f"Oops! Did not found a valid {target} for {name}."
            )

        slots = [SlotSet("mention", None), SlotSet(object_type, name)]
        reset_attribute_slots(slots, object_type, tracker)

        print("\nAttribute query complete\n")
        return slots


class ActionCount(Action):
    """
    Action for counting entities
    """
    def name(self):
        return "action_count"

    def run(self, dispatcher, tracker, domain):
        print("\n* Action: Count Entities.\n")
        graph_database = GraphDatabase()

        # Get object_type
        object_type = get_object_type(tracker)

        # Return if no object_type found
        if object_type is None:
            dispatcher.utter_message(response="utter_rephrase")
            return []

        # Get attributes
        attributes = get_attributes_of_entity(object_type, tracker)

        # Query knowledge base
        print("- Classify object_type:")
        if "relates" in schema[object_type]:
            print("\t- Type: Relations")
            relates = get_relates_of_relations(object_type, tracker)
            print("\n- Counting...")
            count = graph_database.count_relations(object_type, relates, attributes)
        else:
            print("\t- Type: Entities")
            print("\n- Counting...")
            count = graph_database.count_entities(object_type, attributes)

        # Return results
        if count > 0:
            dispatcher.utter_message(
                f"I count {count}."
            )
        else:
            dispatcher.utter_message(
                f"It seems there is none."
            )

        return


class ActionResolveEntity(Action):
    """
    Action for resolving mention.
    """

    def name(self):
        return "action_resolve_entity"

    def run(self, dispatcher, tracker, domain):
        object_type = tracker.get_slot("object_type")
        listed_items = tracker.get_slot("listed_items")

        # utter rephrase if no object_type found
        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # check if the entity is mentioned
        mention = tracker.get_slot("mention")
        if mention is not None:
            value = resolve_mention(tracker)

            if value is not None:
                return [SlotSet(object_type, value), SlotSet("mention", None)]

        # Check if NER recognized entity directly
        value = tracker.get_slot(object_type)
        if value is not None and value in listed_items:
            return [SlotSet(object_type, value), SlotSet("mention", None)]

        dispatcher.utter_template("utter_rephrase", tracker)
        return [SlotSet(object_type, None), SlotSet("mention", None)]


class ResetSlot(Action):
    """
    Reset all slots
    """
    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        print("Reset slots.\n")
        return [AllSlotsReset()]


class ActionGetTargetProduct(Action):
    """
    Get information related to the product of interest
    """
    def name(self) -> Text:
        return "action_get_target_product_details"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()
        slots = []
        print("\n* Action Get Target Product\n")

        attributes = get_attributes_of_entity("product_details", tracker)
        relates = get_relates_of_relations("product_details", tracker)
        # Get existing data from database
        entities = graph_database.get_relations("product_details", relates, attributes)

        # Abort if target entity is not found
        if len(entities) == 0:
            dispatcher.utter_message(response="utter_not_found")
            return [SlotSet("valid", False)]

        # Set data into slots to display
        for relate in schema["product_details"]["relates"]:
            slots.append(SlotSet(relate, entities[0][relate][relate]))

        slots.append(SlotSet("valid", True))
        print("- Current slots:", slots)
        return slots


class ActionGetUpdateProduct(Action):
    """
    Get information related to the product of interest with new information
    """
    def name(self) -> Text:
        return "action_get_update_product_details"

    def run(self, dispatcher, tracker, domain):
        print("\n* Action Get Update Product\n")
        slots = []

        # Copy unchanged information to new slots
        for relate in schema["product_details"]["relates"]:
            if tracker.get_slot("new_" + relate) is None:
                slots.append(SlotSet("new_" + relate, tracker.get_slot(relate)))

        print("- Updated slots:", slots)
        return slots


class ValidateUpdateProductForm(FormValidationAction):
    """
    Validate input from users to adjust form behaviours
    """
    def name(self):
        return "validate_update_product_details_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        """
        Add slot as user's choice
        """
        print("* Validate Update Product Form")
        option = tracker.get_slot("target")
        print("- User option: ", option)

        # Add new slots and questions according to user's choice
        if option == "1":
            print("- Add new_Product slot")
            required_slots = slots_mapped_in_domain + ["new_Product"]
            return required_slots
        elif option == "2":
            print("- Add new_Segment slot")
            required_slots = slots_mapped_in_domain + ["new_Segment"]
            return required_slots
        elif option == "3":
            print("- Add new_TCSS slot")
            required_slots = slots_mapped_in_domain + ["new_TCSS"]
            return required_slots
        elif option == "4":
            print("- Add new_package_tech slot")
            required_slots = slots_mapped_in_domain + ["new_Package_Tech"]
            return required_slots
        elif option == "5":
            print("- Add new_Chip_Attach slot")
            required_slots = slots_mapped_in_domain + ["new_Chip_Attach"]
            return required_slots
        elif option == "6":
            print("- Add new_Tester_Platform slot")
            required_slots = slots_mapped_in_domain + ["new_Tester_Platform"]
            return required_slots
        elif option == "7":
            print("- Add new_AT_Site slot")
            required_slots = slots_mapped_in_domain + ["new_AT_Site"]
            return required_slots
        elif option == "8":
            print("- Add new_Division slot")
            required_slots = slots_mapped_in_domain + ["new_Division"]
            return required_slots
        else:
            required_slots = slots_mapped_in_domain
            return required_slots

    # Functions to instruct how new slots can be extracted from user's message

    @staticmethod
    async def extract_new_Product(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        product = tracker.get_slot("new_Product")
        print("\t- Extracted new product: ", product)
        return {"new_Product": product}

    @staticmethod
    async def extract_new_Segment(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        segment = tracker.get_slot("new_Segment")
        print("\t- Extracted new segment: ", segment)
        return {"new_Segment": segment}

    @staticmethod
    async def extract_new_TCSS(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        tcss = tracker.get_slot("new_TCSS")
        print("\t - Extracted new TC/SS: ", tcss)
        return {"new_TCSS": tcss}

    @staticmethod
    async def extract_new_Package_Tech(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        package_tech = tracker.get_slot("new_Package_Tech")
        print("\t- Extracted new package tech: ", package_tech)
        return {"new_Package_Tech": package_tech}

    @staticmethod
    async def extract_new_Chip_Attach(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        chip_attach = tracker.get_slot("new_Chip_Attach")
        print("\t- Extracted new chip attach: ", chip_attach)
        return {"new_Chip_Attach": chip_attach}

    @staticmethod
    async def extract_new_Tester_Platform(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        tester_platform = tracker.get_slot("new_Tester_Platform")
        print("\t- Extracted new tester platform: ", tester_platform)
        return {"new_Tester_Platform": tester_platform}

    @staticmethod
    async def extract_new_AT_Site(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        at_site = tracker.get_slot("new_AT_Site")
        print("\t- Extracted new AT site: ", at_site)
        return {"new_AT_Site": at_site}

    @staticmethod
    async def extract_new_Division(
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "Dict"
    ) -> Dict[Text, Any]:
        division = tracker.get_slot("new_Division")
        print("\t- Extracted new division: ", division)
        return {"new_Division": division}

    # Validation functions to validate user's input and adjust form behaviours

    @staticmethod
    def validate_target(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new target slot")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        # if slot_value not in range(1, 10):
        #     return {"target": None}

        print("\t- fill slot new_Product")
        return {"target": slot_value}

    @staticmethod
    def validate_new_Product(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Product")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Product")
        return {"new_Product": slot_value}

    @staticmethod
    def validate_new_Segment(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Segment")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Segment")
        return {"new_Segment": slot_value}

    @staticmethod
    def validate_new_TCSS(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new TC/SS")
        print("\t- slot value: ", slot_value)
        intent = tracker.get_intent_of_latest_message()

        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_TCSS")
        return {"new_TCSS": slot_value}

    @staticmethod
    def validate_new_Package_Tech(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Package_Tech")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Package_Tech")
        return {"new_Package_Tech": slot_value}

    @staticmethod
    def validate_new_Chip_Attach(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Chip_Attach")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Chip_Attach")
        return {"new_Chip_Attach": slot_value}

    @staticmethod
    def validate_new_Tester_Platform(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Tester_Platform")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Tester_Platform")
        return {"new_Tester_Platform": slot_value}

    @staticmethod
    def validate_new_AT_Site(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new AT_Site")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_AT_Site")
        return {"new_AT_Site": slot_value}

    @staticmethod
    def validate_new_Division(
            slot_value: Any,
            dispatcher: "CollectingDispatcher",
            tracker: "Tracker",
            domain: "DomainDict"
    ) -> Dict[Text, Any]:
        print("- validate new Division")
        print("\t- slot value: ", slot_value)

        intent = tracker.get_intent_of_latest_message()
        print("\t- intent: ", intent)
        if intent == "out_of_scope":
            print("\t- Stop asking for slots and cancel form")
            return {"requested_slot": None, "cancel": True}

        print("\t- fill slot new_Division")
        return {"new_Division": slot_value}


class ActionSubmitUpdateProduct(Action):
    """
    Action to submit the updated information to the database
    """
    def name(self) -> Text:
        return "action_submit_update_product_details"

    def run(self, dispatcher, tracker, domain):
        print("\n* Submit Form\n")
        graph_database = GraphDatabase()
        object_type = "product_details"
        target = None
        new_data = None
        target_product = tracker.get_slot("Product")

        # Extract the old and new information
        for relate in schema[object_type]["relates"]:
            current_value = tracker.get_slot(relate)
            new_value = tracker.get_slot("new_" + relate)
            print("\n- Current value: ", current_value)
            print("- New value: ", new_value)
            if current_value != new_value:
                target = [{'key': relate, 'value': current_value}]
                new_data = [{'key': relate, 'value': new_value}]

        print("\n- target: ", target)
        print("- new_data: ", new_data)

        # Check if the new entitiy (information) already exists in database
        attributes = [{'key': target[0]['key'], 'value': new_data[0]['value']}]
        print("- attributes", attributes)
        check_object_type = graph_database.map("object_type_mapping", target[0]['key'])
        relate_entities = graph_database.get_entities(check_object_type, attributes)
        print("- relate_entities: ", relate_entities)

        print("\n- Updating...")
        if len(relate_entities) != 0:
            # Replace old data with new data if already exists
            print("\t! New data already in database. Update entity")
            graph_database.update_relations(object_type, target_product, target, new_data)
            # update_relations(object_type, target_product, relates, new_relates
        else:
            # Add the new entity into database then update the old information with the new entity
            print("\t- Insert new entity")
            relate_object_type = graph_database.map("object_type_mapping", target[0]['key'])
            graph_database.insert_entity(relate_object_type, new_data)
            print("\t- Update information of target")
            graph_database.update_relations(object_type, target_product, target, new_data)
            # update_relations(object_type, target_product, relates, new_relates

        dispatcher.utter_message(response="utter_submit")

        print("\nSubmit Complete!")
        return
