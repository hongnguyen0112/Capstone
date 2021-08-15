import logging
from abc import ABC
from typing import List, Dict, Any, Optional, Text
from typedb.client import *

logger = logging.getLogger(__name__)


class KnowledgeBase(object):

    def get_entities(
            self,
            object_type: Text,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            limit: int = 20,
    ) -> List[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented!")

    def get_attribute_of(
            self,
            object_type: Text,
            target_attribute: Text,
            target_relate: Text,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            relates: Optional[List[Dict[Text, Text]]] = None
    ) -> List[Any]:
        raise NotImplementedError("Method is not implemented!")

    def count_entities(
            self,
            object_type: Text,
            attributes: Optional[List[Dict[Text, Text]]] = None
    ) -> int:
        raise NotImplementedError("Method is not implemented!")

    def validate_entity(
            self, object_type, entity, key_attribute, attributes
    ) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented!")

    def map(self, mapping_type: Text, mapping_key: Text) -> Text:
        raise NotImplementedError("Method is not implemented.")

    def get_obj_of_attribute(self, mapping_key: Text) -> Text:
        raise NotImplementedError("Method is not implemented.")


class GraphDatabase(KnowledgeBase, ABC):
    """
    GraphDatabase uses a grakn graph database to encode domain knowledege. Make
    sure to have the graph database set up and the grakn server running.
    """

    def __init__(
            self,
            uri: Text = "typedb-sever:1729",   # Local uri of the local server
            keyspace: Text = "local"        # Name of the database stored in the server
    ):
        self.uri = uri
        self.keyspace = keyspace

    @staticmethod
    def _thing_to_dict(thing, transaction):
        """
        Converts a thing (a grakn object) to a dict for easy retrieval of the thing's
        attributes.
        """
        entity = {"id": thing.get_iid(), "type": thing.get_type().get_label().name()}
        for each in thing.as_remote(transaction).get_has():
            entity[each.get_type().get_label().name()] = each.get_value()
        return entity

    def _execute_entity_query(self, query: Text, object_type: Text) -> List[Dict[Text, Any]]:
        """
        Executes a query that returns a list of entities with all their attributes.
        """
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    # Query entities from database
                    print("\t- Executing TypeQL Entity query: " + query)
                    result_iter = tx.query().match(query)
                    answers = [ans.get(object_type) for ans in result_iter]
                    entities = []
                    # Put entities into list
                    for c in answers:
                        entities.append(self._thing_to_dict(c, tx))
                    return entities

    def _execute_attribute_query(self, query: Text) -> List[Any]:
        """
        Executes a query that returns the value(s) an entity has for a specific
        attribute.
        """
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    # Query attribute from database
                    print("\t- Executing TypeQL Attribute query: " + query)
                    query = "".join(query)
                    iterator = tx.query().match(query)
                    # Get specific value of interest from results
                    answers = [ans.get('v') for ans in iterator]
                    result = [answer.get_value() for answer in answers]
                    return result

    def _execute_relation_query(self, query: Text, relation_name: Text) -> List[Dict[Text, Any]]:
        """
        Execute a query that queries for a relation. All attributes of the relation and
        all entities participating in the relation are part of the result.
        """
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    print("\t- Executing TypeQL Relation query: " + query)
                    result_iter = tx.query().match(query)
                    relations = []
                    # Query knowledge base
                    for concept in result_iter:
                        relation_entity = concept.map().get(relation_name)
                        relation = self._thing_to_dict(relation_entity, tx)
                        # Get roleplayers of the relation
                        for (role_entity, entity_set) \
                                in relation_entity.as_remote(tx).get_players_by_role_type().items():
                            role_label = role_entity.get_label().name()
                            thing = entity_set.pop()
                            relation[role_label] = self._thing_to_dict(thing, tx)
                        relations.append(relation)
                    return relations

    def _execute_count_query(self, query: Text) -> int:
        """
        Executes a query that returns the number of entities.
        """
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    # Execute aggregate match query
                    print("\t- Executing TypeQL Count query: " + query)
                    result = tx.query().match_aggregate(query).get()        # match_aggregate "Count
                    count = result.as_int()
                    print(count)
                    return count

    @staticmethod
    def _get_attribute_clause(attributes: Optional[List[Dict[Text, Text]]] = None) -> Text:
        """
        Construct the attribute clause.
        :param attributes: attributes
        :return: attribute clause as string
        """
        clause = ""
        if attributes:
            # Format: , has key 'value',
            clause = ",".join([f"has {a['key']} '{a['value']}'" for a in attributes])
            clause = ", " + clause
        return clause

    @staticmethod
    def _get_relates_clause(relates: Optional[List[Dict[Text, Text]]] = None) -> Text:
        """
        Construct the criteria clause.
        :param relates: attributes
        :return: criteria clause as string
        """
        clause = ""
        if relates:
            # Format: $attribute_info isa attribute_info, has attribute 'value';
            clause = "".join([f"${a['key']}_info isa {a['key']}_info, has {a['key']} '{a['value']}';" for a in relates])
            clause = "" + clause
        return clause

    @staticmethod
    def _get_target_relates_clause(target_relates: Text) -> Text:
        """
        Construct the criteria match clause.
        :param target_relates: target related entity
        :return: criteria match clause as string
        """
        clause = ""
        if target_relates:
            # Format: $relates_info isa relates_info, has relates $v;
            clause = "".join(f"${target_relates}_info isa {target_relates}_info, has {target_relates} $v;")
            clause = "" + clause
        return clause

    @staticmethod
    def _get_target_attribute_clause(target_attribute: Text) -> Text:
        """
        Construct the criteria match clause.
        :param target_attribute: target related entity
        :return: criteria match clause as string
        """
        clause = ""
        if target_attribute:
            # Format: has attribute $v;
            clause = "".join(f"has {target_attribute} $v")
            clause = ", " + clause
        return clause

    @staticmethod
    def _get_relates_match(relates: Optional[List[Dict[Text, Text]]] = None) -> Text:
        """
        Construct the criteria match clause.
        :param relates: attributes
        :return: criteria match clause as string
        """
        clause = ""
        if relates:
            # Format: relates: $relates_info
            clause = ", ".join([f"{a['key']}: ${a['key']}_info " for a in relates])
            clause = "" + clause
            # $attribute_info isa attribute_info, has attribute 'value';

        return clause

    @staticmethod
    def _get_target_relates_match(target_relate: Text) -> Text:
        """
        Construct the criteria match clause.
        :param target_relate: attributes
        :return: criteria match clause as string
        """
        clause = ""
        if target_relate:
            # Format: relates: $relates_info
            clause = "".join(f"{target_relate}: ${target_relate}_info")
            clause = ", " + clause
            # $attribute_info isa attribute_info, has attribute 'value';

        return clause

    def get_attribute_of(
            self,
            object_type: Text,
            target_attribute: Text,
            target_relate: Text,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            relates: Optional[List[Dict[Text, Text]]] = None
    ) -> List[Any]:
        """
        Get the value of the given attribute for the provided entity.
        :param object_type: entity type
        :param target_attribute: attribute of interest
        :param target_relate: related entity of interest
        :param attributes: provided attribute
        :param relates: provided relates
        :return: the value of the attribute
        """
        # Query without relates clauses if none is given
        if relates is None and target_relate is None:
            attribute_clause = self._get_attribute_clause(attributes)
            target_attribute_clause = self._get_target_attribute_clause(target_attribute)
            return self._execute_attribute_query(
                f"match "
                f"${object_type} "
                f"isa {object_type}{attribute_clause}{target_attribute_clause}; "
                f"get $v;"
            )

        # Else, query with given relates and optional attributes
        relates_clause = self._get_relates_clause(relates)
        match_relates = self._get_relates_match(relates)
        match_target_relate = self._get_target_relates_match(target_relate)
        attribute_clause = self._get_attribute_clause(attributes)
        target_relate_clause = self._get_target_relates_clause(target_relate)
        target_attribute_clause = self._get_target_attribute_clause(target_attribute)
        return self._execute_attribute_query(
            f"match "
            f"{relates_clause} "
            f"{target_relate_clause} "
            f"${object_type} ({match_relates}{match_target_relate}) "
            f"isa {object_type}{attribute_clause}{target_attribute_clause}; "
            f"get $v;"
        )
    # Example of complete query
    # match
    # $Product_info isa Product_info, has Product 'Product AONE';
    # $Cycle_info isa Cycle_info, has Cycle 'Apr_21';
    # $Phase_info isa Phase_info, has Phase 'ES';
    # $Comment_info isa Comment_info, has Comment $v;
    # (Product: $Product_info, Cycle: $Cycle_info, Phase: $Phase_info, Comment: $Comment_info)
    # isa production_log, has WW $ww;
    # get $v;

    def get_entities(
            self,
            object_type: Text,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            limit: int = 20
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for entities of the given type. Restrict the entities
        by the provided attributes, if any attributes are given.
        :param object_type: the entity type
        :param attributes: list of attributes
        :param limit: maximum number of entities to return
        :return: list of entities
        """
        print("\t- object_type: ", object_type)
        print("\t- attributes: ", attributes)
        attribute_clause = self._get_attribute_clause(attributes)
        return self._execute_entity_query(
            f"match "
            f"${object_type} isa {object_type}{attribute_clause};"
            f"get ${object_type};",
            object_type
        )[:limit]

    def get_relations(
            self,
            object_type: Text,
            relates: Optional[List[Dict[Text, Text]]] = None,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            limit: int = 20
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for relations of the given type. Restrict the relations
        by the provided relates and attribute, if any are given.
        :param object_type: the entity type
        :param relates: list of relates
        :param attributes: list of attributes
        :param limit: maximum number of entities to return
        :return: list of entities
        """
        print("\t- object_type: ", object_type)
        print("\t- attributes: ", attributes)
        print("\t- relates: ", relates)
        attribute_clause = self._get_attribute_clause(attributes)
        relates_match_clause = self._get_relates_clause(relates)
        match_relates = self._get_relates_match(relates)
        return self._execute_relation_query(
            f"match "
            f"{relates_match_clause} "
            f"${object_type} ({match_relates}) "
            f"isa {object_type}{attribute_clause}; "
            f"get ${object_type};",
            object_type
        )[:limit]

    def count_entities(self, object_type: Text, attributes: Optional[List[Dict[Text, Text]]] = None) -> int:
        """
        Query the graph database to count entities of the given type.
        Restrict the entities by the provided attributes, if any attributes are given.
        :param object_type: the entity type
        :param attributes: list of attributes
        :return: number of entities
        """
        print("\t- object_type: ", object_type)
        print("\t- attributes: ", attributes)
        attribute_clause = self._get_attribute_clause(attributes)
        return self._execute_count_query(
            f"match "
            f"${object_type} isa {object_type}{attribute_clause};"
            f"get ${object_type}; count;"
        )

    def count_relations(
            self,
            object_type: Text,
            relates: Optional[List[Dict[Text, Text]]] = None,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> int:
        """
        Query the graph database to count relations of the given type.
        Restrict the relations by the provided relates and attributes, if any are given.
        :param object_type: the entity type
        :param relates: list of relates
        :param attributes: list of attributes
        :return: list of entities
        """
        print("\t- object_type: ", object_type)
        print("\t- attributes: ", attributes)
        print("\t- relates: ", relates)
        # Query without relations clauses if none is given
        if relates is None:
            attribute_clause = self._get_attribute_clause(attributes)
            return self._execute_count_query(
                f"match "
                f"${object_type} "
                f"isa {object_type}{attribute_clause}; "
                f"get ${object_type}; count;"
            )
        # Else, match relations and attributes
        attribute_clause = self._get_attribute_clause(attributes)
        relates_match_clause = self._get_relates_clause(relates)
        match_relates = self._get_relates_match(relates)
        return self._execute_count_query(
            f"match "
            f"{relates_match_clause} "
            f"${object_type} ({match_relates}) "
            f"isa {object_type}{attribute_clause}; "
            f"get ${object_type}; count;"
        )

    def map(self, mapping_type: Text, mapping_key: Text) -> Text:
        """
        Query the given mapping table for the provided key.
        :param mapping_type: the name of the mapping table
        :param mapping_key: the mapping key
        :return: the mapping value
        """
        print("\t- Mapping value:")
        value = self._execute_attribute_query(
            f"match "
            f"$mapping isa {mapping_type}, "
            f"has mapping_key '{mapping_key}', "
            f"has mapping_value $v;"
            f"get $v;"
        )
        if len(value) == 0:
            return
        if value and len(value) == 1:
            print("\t- Mapped value: ", value[0])
            return value[0]

    def get_obj_of_attribute(self, mapping_key: Text) -> Text:
        """
        Query the attribute mapping table for the provided key to get object_type.
        :param mapping_key: the mapping key
        :return: the mapped object_type of attribute
        """
        print("\t- Mapping value:")
        value = self._execute_attribute_query(
            f"match "
            f"$mapping isa attribute_mapping, "
            f"has mapping_key '{mapping_key}', "
            f"has object_type $v;"
            f"get $v;"
        )
        if len(value) == 0:
            return
        if value and len(value) == 1:
            print("\t- Mapped object_type: ", value[0])
            return value[0]

    def validate_entity(
            self, object_type, entity, key_attribute, attributes
    ) -> Dict[Text, Any]:
        """
        Validates if the given entity has all provided attribute values.
        :param object_type: entity type
        :param entity: name of the entity
        :param key_attribute: key attribute of entity
        :param attributes: attributes
        :return: the found entity
        """
        attribute_clause = self._get_attribute_clause(attributes)

        value = self._execute_entity_query(
            f"match "
            f"${object_type} isa {object_type}{attribute_clause}, "
            f"has {key_attribute} '{entity}'; "
            f"get ${object_type};",
            object_type
        )

        if value and len(value) == 1:
            return value[0]
