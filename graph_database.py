import logging
from abc import ABC
from typing import List, Dict, Any, Optional, Text
from grakn.client import Grakn, SessionType, TransactionType

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
            key_attribute: Text,
            entity: Text,
            attributes: Text
    ) -> List[Any]:
        raise NotImplementedError("Method is not implemented!")

    def validate_entity(
            self, object_type, entity, key_attribute, attributes
    ) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented!")

    def map(self, mapping_type: Text, mapping_key: Text) -> Text:
        raise NotImplementedError("Method is not implemented.")


class GraphDatabase(KnowledgeBase, ABC):
    """
    GraphDatabase uses a grakn graph database to encode domain knowledege. Make
    sure to have the graph database set up and the grakn server running.
    """

    def __init__(
            self,
            uri: Text = "localhost:1729",
            keyspace: Text = "product"
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
        with Grakn.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    logger.debug("Entity: Executing Graql query: " + query)
                    result_iter = tx.query().match(query)
                    answers = [ans.get(object_type) for ans in result_iter]
                    entities = []
                    for c in answers:
                        entities.append(self._thing_to_dict(c, tx))

                    return entities

    def _execute_attribute_query(self, query: Text) -> List[Any]:
        """
        Executes a query that returns the value(s) an entity has for a specific
        attribute.
        """
        with Grakn.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:
                    print("Attribute: Executing Graql Query: " + query)
                    query = "".join(query)
                    iterator = tx.query().match(query)
                    answers = [ans.get('v') for ans in iterator]
                    result = [answer.get_value() for answer in answers]

                    return result

    def _execute_relation_query(
            self,
            query: Text,
            relation_name: Text
    ) -> List[Dict[Text, Any]]:
        """
        Execute a query that queries for a relation. All attributes of the relation and
        all entities participating in the relation are part of the result.
        """
        with Grakn.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:

                    print("Relation: Executing Graql Query: " + query)
                    result_iter = tx.query().match(query)
                    relations = []

                    for concept in result_iter:
                        relation_entity = concept.map().get(relation_name)
                        print("Type: ", relation_entity.get_type())
                        relation = self._thing_to_dict(relation_entity, tx)

                        for (role_entity, entity_set) in relation_entity.as_remote(
                                tx).get_players_by_role_type().items():
                            role_label = role_entity.get_label().name()
                            thing = entity_set.pop()
                            relation[role_label] = self._thing_to_dict(thing, tx)
                        relations.append(relation)

                    return relations

    @staticmethod
    def _get_attribute_clause(
            attributes: Optional[List[Dict[Text, Text]]] = None
    ) -> Text:
        """
        Construct the attribute clause.
        :param attributes: attributes
        :return: attribute clause as string
        """
        clause = ""

        if attributes:
            clause = ",".join([f"has {a['key']} '{a['value']}'" for a in attributes])
            clause = ", " + clause
            # , has key 'value',

        return clause

    def _get_attribute_of(
            self,
            object_type: Text,
            key_attribute: Text,
            entity: Text,
            attributes: Text
    ) -> List[Any]:
        """
        Get the value of the given attribute for the provided entity.
        :param object_type: entity type
        :param key_attribute: key attribute of entity
        :param entity: name of the entity
        :param attributes: attribute of interest
        :return: the value of the attribute
        """
        return self._execute_attribute_query(
            f"""
                match
                    ${object_type} isa {object_type},
                    has {key_attribute} '{entity}',
                    has {attributes} $a;
                get $a
            """
        )

    def _get_cycle_entities(
            self, attributes: Optional[List[Dict[Text, Text]]] = None
    ) -> List[Dict[Text, Any]]:

        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get cycle")

        return self._execute_relation_query(
            f"match "
            f"$include_cycle (product: $product, cycle: $cycle_info) "
            f"isa include_cycle{attributes_clause}; "
            f"get $include_cycle;",
            "include_cycle"
        )

    def _get_testerplatform_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get tester platform relation")
        return self._execute_relation_query(
            f"match "
            f"$include_testerplatform (product: $product, Tester_Platform: $testerplatform_info)"
            f"isa include_testerplatform{attributes_clause};"
            f"get $include_testerplatform;",
            "include_testerplatform"
        )

    def _get_segment_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get segment relation")
        return self._execute_relation_query(
            f"match "
            f"$include_segment (product: $product, Segment: $segment_info)"
            f"isa include_segment{attributes_clause};"
            f"get $include_segment;",
            "include_segment"
        )

    def _get_division_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get division relation")
        return self._execute_relation_query(
            f"match "
            f"$include_division (product: $product, Division: $division_info)"
            f"isa include_division{attributes_clause};"
            f"get $include_division;",
            "include_division"
        )

    def _get_package_tech_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get package_tech relation")
        return self._execute_relation_query(
            f"match "
            f"$include_package_tech (product: $product, Package_Tech: $package_tech_info)"
            f"isa include_package_tech{attributes_clause};"
            f"get $include_package_tech;",
            "include_package_tech"
        )

    def _get_chip_attach_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get chip_attach relation")
        return self._execute_relation_query(
            f"match "
            f"$include_chip_attach (product: $product, Chip_Attach: $chip_attach_info)"
            f"isa include_chip_attach{attributes_clause};"
            f"get $include_chip_attach;",
            "include_chip_attach"
        )

    def _get_at_site_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get AT_Site relation")
        return self._execute_relation_query(
            f"match "
            f"$include_at_site (product: $product, at_site: $at_site_info)"
            f"isa include_at_site{attributes_clause};"
            f"get $include_at_site;",
            "include_at_site"
        )

    def _get_tcss_entities(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get TC/SS entities")
        return self._execute_relation_query(
            f"match "
            f"$include_tcss (product: $product, tcss: $tcss_info)"
            f"isa include_tcss{attributes_clause};"
            f"get $include_tcss;",
            "include_tcss"
        )

    def _get_comment_info(
            self,
            attributes: Optional[List[Dict[Text, Text]]] = None,
            limit: int = 20
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for comments. Restrict the comment
        by the provided attributes, if any attributes are given.
        :param attributes: list of attributes
        :param limit: maximum number of comments to return
        :return: list of comments and date
        """
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get product entities")
        return self._execute_entity_query(
            f"match "
            f"$comment_info isa comment_info, has comment != ''{attributes_clause}; "
            f"get $comment_info;",
            "comment_info"
        )[:limit]

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
        print("get_entities - object_type: ", object_type)
        print("get_entities - attributes: ", attributes)

        if object_type == "include_cycle":
            return self._get_cycle_entities(attributes)
        elif object_type == "include_testerplatform":
            return self._get_testerplatform_entities(attributes)
        elif object_type == "include_segment":
            return self._get_segment_entities(attributes)
        elif object_type == "include_division":
            return self._get_division_entities(attributes)
        elif object_type == "include_package_tech":
            return self._get_package_tech_entities(attributes)
        elif object_type == "include_chip_attach":
            return self._get_chip_attach_entities(attributes)
        elif object_type == "include_tcss":
            return self._get_tcss_entities(attributes)
        elif object_type == "include_at_site":
            return self._get_at_site_entities(attributes)
        elif object_type == "comment_info":
            return self._get_comment_info(attributes)

        attribute_clause = self._get_attribute_clause(attributes)

        return self._execute_entity_query(
            f"match "
            f"${object_type} isa {object_type}{attribute_clause};"
            f"get ${object_type};",
            object_type
        )[:limit]

    def map(
            self,
            mapping_type: Text,
            mapping_key: Text
    ) -> Text:
        """
        Query the given mapping table for the provided key.
        :param mapping_type: the name of the mapping table
        :param mapping_key: the mapping key
        :return: the mapping value
        """
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
            print("mapping_value: ", value[0])
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
