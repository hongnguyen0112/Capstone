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
        idx = int(graph_database.map("mention-mapping", mention))
        if type(idx) is int and idx < len(listed_items):
            return listed_items[idx]


def get_entity_type(tracker: Tracker) -> Text:
    graph_database = GraphDatabase()
    entity_type = tracker.get_slot("entity_type")
    return graph_database.map("entity-type-mapping", entity_type)


def get_attribute(tracker: Tracker) -> Text:
    graph_database = GraphDatabase()
    attribute = tracker.get_slot("attribute")
    return graph_database.map("attribute-mapping", attribute)


def get_entity_name(tracker: Tracker, entity_type: Text):
    mention = tracker.get_slot("mention")
    if mention is not None:
        return resolve_mention(tracker)
    entity_name = tracker.get_slot(entity_type)
    if entity_name:
        return entity_name
    listed_items = tracker.get_slot("listed_items")
    attributes = get_attributes_of_entity(entity_type, tracker)
    if listed_items and attributes:
        for entity in listed_items:
            graph_database = GraphDatabase()
            for entity in listed_items:
                key_attr = schema[entity_type]["key"]
                result = graph_database.validate_entity(
                    entity_type, entity, key_attr, attributes
                )
                if result is not None:
                    return to_str(result, key_attr)
    return None


def get_attributes_of_entity(entity_type, tracker):
    attributes = []
    if entity_type in schema:
        for attr in schema[entity_type]["attributes"]:
            attr_val = tracker.get_slot(attr.replace("-", "_"))
            if attr_val is not None:
                attributes.append({"key": attr, "value": attr_val})
    return attributes


def reset_attribute_slots(slots, entity_type, tracker):
    if entity_type in schema:
        for attr in schema[entity_type]["attributes"]:
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
        for k in key.split("."):
            _e = _e[k]

        if "balance" in key or "amount" in key:
            v_list.append(f"{str(_e)} €")
        elif "date" in key:
            v_list.append(_e.strftime("%d.%m.%Y (%H:%M:%S)"))
        else:
            v_list.append(str(_e))
    return ", ".join(v_list)


class ActionQueryEntities(Action):

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        entity_type = get_entity_type(tracker)
        
        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
            
        attributes = get_attributes_of_entity(entity_type, tracker)
        
        entities = graph_database.get_entities(entity_type, attributes)
        
        if not entities:
            dispatcher.utter_template(
                "I could not find any entities for '{}'.".format(entity_type), tracker
            )
            return []
        
        entity_representation = schema[entity_type]["representation"]

        dispatcher.utter_message(
            "Found the following '{}' entities: ".format(entity_type)
        )
        
        sorted_entities = sorted([to_str(e, entity_representation) for e in entities])
        for i, e in enumerate(sorted_entities):
            dispatcher.utter_message(f"{i + 1}: {e}")

        # set slots
        # set the entities slot in order to resolve references to one of the found
        # entities later on
        entity_key = schema[entity_type]["key"]
        
        slots = [
            SlotSet("entity_type", entity_type),
            SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        ]
        
        # if only one entity was found, that the slot of that entity type to the found entity
        if len(entities) == 1:
            slots.sappend(SlotSet(entity_type, to_str(entities[0], entity_key)))

        reset_attribute_slots(slots, entity_type, tracker)
        
        return slots   

    
class ActionQueryAttribute(Action):
    def name(self):
        return "action_query_attributes"
    def run(self, dispatcher, tracker, domain):
        graph_database = GraphDatabase()

        entity_type = get_entity_type(tracker)
        
        if entity_type is None:
            dispatcher.utter_template("utter_rephrase",tracker)
            return []
        
        name = get_entity_type(tracker,entity_type)
        attribute = get_attribute(tracker)
        
        if name is None or attribute is None:
            dispatcher.utter_template("utter_rephrase",tracker)
            slots = [SlotSet("mention", None)]
            reset_attribute_slots(slots, entity_type, tracker)
            return slots

        key_attribute = schema[entity_type]["key"]
        value = graph_database.get_attribute_of(entity_type,key_attribute,name,attribute )

        


#Action for resolving a mention
class ActionResolveEntity(Action):
    def name (self):
        return "action_resolve_entity"
    
    def run(self, dispatcher, tracker, domain):
        entity_type = tracker.get_slot("entity_type")
        listed_items = tracker.get_slot("listed_items")

        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []
        
        mention = tracker.get_slot("mention")
        if mention is not None:
            value = resolve_mention(tracker)
            if value is not None: 
                return [SlotSet(entity_type, value), SlotSet("mention", None)]
        
        # Check if NER recognized entity directly
        value = tracker.get_slot(entity_type)
        if value is not None and value in listed_items:
            return [SlotSet(entity_type, value), SlotSet("mention", None)]

        dispatcher.utter_template("utter_rephrase", tracker)
        return [SlotSet(entity_type, None), SlotSet("mention", None)]