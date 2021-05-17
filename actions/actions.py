# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# -*- coding: utf-8 -*-
from typing import Text, Dict, Any, List, Union

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker

from schema import schema
from graph_database import GraphDatabase

class ActionQueryAttribute(Action):
    def name(self):
        return "action_query_attribute"

    def run(self, dispatcher, tracker, domain):
        pass