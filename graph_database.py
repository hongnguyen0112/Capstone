import logging
from typing import List, Dict, Any, Optional, Text
from grakn.client import Grakn, SessionType, TransactionType

logger = logging.getLogger(__name__)


class KnowledgeBase(object):

    def get_entities (
        self,
        object_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 20,
    ) -> List[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented!")


    def get_attribute_of (
        self,
        object_type: Text,
        key_attribute: Text,
        entity: Text,
        attributes: Text
    ) -> List[Any]:
        raise NotImplementedError("Method is not implemented!")


    def validate_entity (
        self, object_type, entity, key_attribute, attributes
    ) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented!")
    
    def map(self, mapping_type: Text, mapping_key: Text) -> Text:
        raise NotImplementedError("Method is not implemented.")
    

class GraphDatabase(KnowledgeBase):
    """
    GraphDatabase uses a grakn graph database to encode domain knowledege. Make
    sure to have the graph database set up and the grakn server running.
    """

    def __init__ (
        self, 
        uri: Text = "localhost:1729",
        keyspace: Text = "product"
    ):
        self.uri = uri
        self.keyspace = keyspace


    def _thing_to_dict(self, thing, transaction):
        """
        Converts a thing (a grakn object) to a dict for easy retrieval of the thing's
        attributes.
        """
        entity = {"id": thing.get_iid(), "type": thing.get_type().get_label().name()}

        for each in thing.as_remote(transaction).get_has():
            entity[each.get_type().get_label().name()] = each.get_value()

        return entity


    def _execute_entity_query(self, query: Text) -> List[Dict[Text, Any]]:
        """
        Executes a query that returns a list of entities with all their attributes.
        """
        with Grakn.core_client(self.uri) as client:
            with client.session(self.keyspace, SessionType.DATA) as session:
                with session.transaction(TransactionType.READ) as tx:

                    logger.debug("Entity: Executing Graql query: " + query)
                    result_iter = tx.query().match(query)
                    answers = [ans.get("product") for ans in result_iter]
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
                        relation = self._thing_to_dict(relation_entity)

                        for (role_entity, entity_set) in relation_entity.role_players_map().items():
                            role_label = role_entity.label()
                            thing = entity_set.pop()
                            relation[role_label] = self._thing_to_dict(thing)
                        relations.append(relation)

                    return relations


    def _get_attribute_clause (
        self,
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
            #, has key 'value', 

        return clause
    

    def _get_attribute_of (
        self,
        object_type: Text,
        key_attribute: Text,
        entity: Text,
        attributes: Text
    ) -> List[Any]:
        """
        Get the value of the given attribute for the provided entity.
        :param entity_type: entity type
        :param key_attribute: key attribute of entity
        :param entity: name of the entity
        :param attribute: attribute of interest
        :return: the value of the attribute
        """
        return self._execute_attribute_query (
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

        return self._execute_relation_query (
            f"match "
            f"$include_cycle (product: $pr, cycle_info: $cyi) "
            f"isa include_cycle{attributes_clause}; "
            f"get $include_cycle;",
            "include_cycle"
        )


    def _get_product_entities (
        self,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 20
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for product. Restrict the product
        by the provided attributes, if any attributes are given.
        :param attributes: list of attributes
        :param limit: maximum number of products to return
        :return: list of products
        """
        attributes_clause = self._get_attribute_clause(attributes)
        logger.debug("Get product entities")
        return self._execute_entity_query (
            f"match "
            f"$product isa product{attributes_clause}; "
            f"get $product;"
        )[:limit]


    def get_entities (
        self, 
        object_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 20
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for entities of the given type. Restrict the entities
        by the provided attributes, if any attributes are given.
        :param entity_type: the entity type
        :param attributes: list of attributes
        :param limit: maximum number of entities to return
        :return: list of entities
        """
        if object_type == "product":
            return self._get_product_entities(attributes, limit)
        if object_type == "cycle_info":
            return self._get_cycle_entities(attributes)

        attribute_clause = self._get_attribute_clause(attributes)

        return self._execute_entity_query(
            f"match "
            f"${object_type} isa {object_type}{attribute_clause};"
            f"get ${object_type};"
        )[:limit]


    def map (
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

        print("mapping_value: ", value[0])

        if value and len(value) == 1:
            return value[0]
    

    def validate_entity(
        self, object_type, entity, key_attribute, attributes
    ) -> Dict[Text, Any]:
        """
        Validates if the given entity has all provided attribute values.
        :param entity_type: entity type
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
            f"get ${object_type};"
        )
        
        if value and len(value) == 1:
            return value[0]
    