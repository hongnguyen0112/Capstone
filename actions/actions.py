# -*- coding: utf-8 -*-
from typing import Text, Dict, Any, List, Union
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk import Action, Tracker
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
    print("get_object_type: ", object_type)
    return graph_database.map("object_type_mapping", object_type)


def get_attribute(tracker: Tracker) -> Text:
    """
    Get the attribute mentioned by the user. As the user may use a synonym for
    an attribute, we need to map the mentioned attribute to the
    attribute name used in the knowledge base.
    :param tracker: tracker
    :return: attribute (same type as used in the knowledge base)
    """
    graph_database = GraphDatabase()
    attribute = tracker.get_slot("attribute")
    return graph_database.map("attribute_mapping", attribute)


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
    mention = tracker.get_slot("mention")

    if mention is not None:
        return resolve_mention(tracker)

    entity_name = tracker.get_slot(object_type)

    if entity_name:
        return entity_name

    listed_items = tracker.get_slot("listed_items")
    attributes = get_attributes_of_entity(object_type, tracker)

    if listed_items and attributes:
        for entity in listed_items:
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
    print("get_attributes_of_entities: ", attributes)
    return attributes


def reset_attribute_slots(slots, object_type, tracker):
    # check what attributes the NER found for entity type
    if object_type in schema:

        for attr in schema[object_type]["attributes"]:
            attr = attr.replace("-", "_")
            attr_val = tracker.get_slot(attr)

            if attr_val is not None:
                slots.append(SlotSet(attr, None))
    print("reset_attribute_slots: ", slots)
    return slots


def to_str(
        entity: Dict[Text, Any],
        entity_keys: Union[Text, List[Text]]
    ) -> Text:
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
    print("Got following entities:")
    for key in entity_keys:
        _e = entity
        
        for k in key.split("."):
            print(_e)
            _e = _e[k]

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
        graph_database = GraphDatabase()

        # need to know the object_type we are looking for
        object_type = get_object_type(tracker)
        print("actions_query_entity-object_type: ", object_type)
        
        # utter rephrase if found no object_type recognised
        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # check what attributes the NER found for entity type
        attributes = get_attributes_of_entity(object_type, tracker)
        print("actions_query_entity-attributes: ", attributes)

        # query knowledge base
        entities = graph_database.get_entities(object_type, attributes)

        if object_type == "include_cycle":
            cycle = tracker.get_slot("cycle")
            entities = self._filter_cycle_entities(entities, cycle)
        if object_type == "include_testerplatform":
            testerplatform = tracker.get_slot("testerplatform")
            entities = self._filter_testerplatform_entities(entities, testerplatform)
        if object_type == "include_segment":
            segment = tracker.get_slot("segment")
            entities = self._filter_segment_entities(entities, segment)
        
        # utter message if no instance is found with the object_type
        if not entities:
            dispatcher.utter_template(
                "I could not find any entities for {}.".format(object_type), tracker
            )
            return []
        
        """
        Utter response and list all found instances 
        """
        # use the 'representation' attributes to print an entity
        entity_representation = schema[object_type]["representation"]

        dispatcher.utter_message(
            "Found the following {} entities: ".format(object_type)
        )
        
        sorted_entities = sorted([to_str(e, entity_representation) for e in entities])
        for i, e in enumerate(sorted_entities):
            dispatcher.utter_message(f"{i + 1}: {e}")

        # set slots
        # set the entities slot in order to resolve references to one of the found
        # entities later on
        entity_key = schema[object_type]["key"]
        
        #Number items in result list
        slots = [
            SlotSet("object_type", object_type),
            SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        ]
        
        # if only one entity was found, that the slot of that entity type to the found entity
        if len(entities) == 1:
            slots.append(SlotSet(object_type, to_str(entities[0], entity_key)))

        reset_attribute_slots(slots, object_type, tracker)
        
        return slots   
    

    def _filter_cycle_entities (
        self, entities: List[Dict[Text, Any]], cycle: Text
    ) -> List[Dict[Text, Any]]:
        """
        Filter out all cycle that do not belong to the provided cycle.
        :param entities: list of entities
        :param account_number: provided cycle
        :return: list of filtered entities with max. 20 entries
        """
        if cycle is not None:
            filtered_entities = []
            for entity in entities:
                if entity["cycle"]["cycle"] == cycle:
                    filtered_entities.append(entity)
            return filtered_entities[:20]
        
        return entities[:20]
    
    def _filter_testerplatform_entities (
        self, entities: List[Dict[Text, Any]], testerplatform: Text
    ) -> List[Dict[Text, Any]]:
        if testerplatform is not None:
            filtered_entities = []
            for entity in entities:
                if entity["Tester_Platform"]["Tester_Platform"] == testerplatform:
                    filtered_entities.append(entity)
            return filtered_entities[:20]
        return entities[:20]

    def _filter_segment_entities (
        self, entities: List[Dict[Text, Any]], segment: Text
    ) -> List[Dict[Text, Any]]:
        if segment is not None:
            filtered_entities = []
            for entity in entities:
                if entity["Segment"]["Segment"] == segment:
                    filtered_entities.append(entity)
            return filtered_entities[:20]
        return entities[:20]

    
class ActionQueryAttribute(Action):
    """
    Action for querying a specific attribute of an entity.
    """

    def name(self):
        return "action_query_attribute"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        # get entity type of entity
        object_type = get_object_type(tracker)
        
        # utter rephrase if no object_type found
        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
        
        # get name of entity and attribute of interest
        name = get_object_type(tracker, object_type)
        attribute = get_attribute(tracker)
        
        # utter rephrase if no name or attribute recognised
        if name is None or attribute is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            slots = [SlotSet("mention", None)]
            reset_attribute_slots(slots, object_type, tracker)
            return slots

        # query knowledge base
        key_attribute = schema[object_type]["key"]
        value = graph_database.get_attribute_of(
            object_type, key_attribute, name, attribute 
        )

        # utter response
        if value is not None and len(value) == 1:
            dispatcher.utter_message (
                f"{name} has the value '{value[0]}' for attribute '{attribute}'."
            )
        else:
            dispatcher.utter_message (
                f"Did not found a valid value for attribute {attribute} for entity'{name}'."
            )
        
        slots = [SlotSet("mention", None), SlotSet(object_type, name)]
        reset_attribute_slots(slots, object_type, tracker)
        return slots
        

#Action for resolving a mention
class ActionResolveEntity(Action):
    """
    Action for resolving mention.
    """

    def name (self):
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

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("object_type", None),
                SlotSet("cycle", None)]