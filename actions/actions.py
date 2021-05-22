# -*- coding: utf-8 -*-
from typing import Text, Dict, Any, List, Union
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from schema import schema
from graph_database import GraphDatabase

def resolve_mention(tracker: Tracker) -> Text:
    graph_database = GraphDatabase()
    mention = tracker.get_slot("mention")
    listed_items = tracker.get_slot("listed_items")
    if mention is not None and listed_items is not None:
        idx = int(graph_database.map("mention_mapping", mention))
        if type(idx) is int and idx < len(listed_items):
            return listed_items[idx]


def get_object_type(tracker: Tracker) -> Text:
    graph_database = GraphDatabase()
    object_type = tracker.get_slot("object_type")
    return graph_database.map("object_type_mapping", object_type)


def get_attribute(tracker: Tracker) -> Text:
    graph_database = GraphDatabase()
    attribute = tracker.get_slot("attribute")
    return graph_database.map("attribute_mapping", attribute)


def get_entity_name(tracker: Tracker, object_type: Text):
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
    attributes = []
    if object_type in schema:
        for attr in schema[object_type]["attributes"]:
            attr_val = tracker.get_slot(attr.replace("-", "_"))
            if attr_val is not None:
                attributes.append({"key": attr, "value": attr_val})
    return attributes


def reset_attribute_slots(slots, object_type, tracker):
    if object_type in schema:
        for attr in schema[object_type]["attributes"]:
            attr = attr.replace("-", "_")
            attr_val = tracker.get_slot(attr)
            if attr_val is not None:
                slots.append(SlotSet(attr, None))
    return slots


def to_str(
        entity: Dict[Text, Any],
        entity_keys: Union[Text, List[Text]]
    ) -> Text:
    if isinstance(entity_keys, str):
        entity_keys = [entity_keys]
    v_list = []
    for key in entity_keys:
        _e = entity
        print("Got following entities:")
        for k in key.split("."):
            print(_e)
            _e = _e[k]
        v_list.append(str(_e))
    return ", ".join(v_list)


class ActionQueryEntities(Action):

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        object_type = get_object_type(tracker)
        
        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
            
        attributes = get_attributes_of_entity(object_type, tracker)
        
        entities = graph_database.get_entities(object_type, attributes)
        
        if not entities:
            dispatcher.utter_template(
                "I could not find any entities for '{}'.".format(object_type), tracker
            )
            return []
        
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
        
        slots = [
            SlotSet("object_type", object_type),
            SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        ]
        
        # if only one entity was found, that the slot of that entity type to the found entity
        if len(entities) == 1:
            slots.append(SlotSet(object_type, to_str(entities[0], entity_key)))

        reset_attribute_slots(slots, object_type, tracker)
        
        return slots   

    
class ActionQueryAttribute(Action):

    def name(self):
        return "action_query_attribute"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        object_type = get_object_type(tracker)
        
        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
        
        name = get_object_type(tracker, object_type)
        attribute = get_attribute(tracker)
        
        if name is None and attribute is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            slots = [SlotSet("mention", None)]
            reset_attribute_slots(slots, object_type, tracker)
            return slots

        key_attribute = schema[object_type]["key"]
        value = graph_database.get_attribute_of(
            object_type, key_attribute, name, attribute 
        )

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
    def name (self):
        return "action_resolve_entity"
    
    def run(self, dispatcher, tracker, domain):
        object_type = tracker.get_slot("object_type")
        listed_items = tracker.get_slot("listed_items")

        if object_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
        
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