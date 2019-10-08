"""Serialize/deserialize Space into the data storage"""

from .ontology.generic import ThingDB
from .ontology.manager import PREFIX
from .schemas import ModelSchema
from .utils import str_insert, str_filter, generate_id
from .ontology.manager import SPARQLOP
from .db_output import OutputDB


class ModelDB(ThingDB):
    """A class to handle models in the data storage solution"""

    # Dictionary for direct relations - values
    FIELD_TO_RELATION = {
        'id': PREFIX.SERVICES.alias_uri('id'),
        'name': PREFIX.SERVICES.alias_uri('name'),
        'description': PREFIX.SERVICES.alias_uri('description'),
    }

    # Dicts for attributes that require access to additional concepts/instances
    LINKS = {
        'service_id': PREFIX.SERVICES.alias_uri('partOfService'),
        'event_output_ids': PREFIX.SERVICES.alias_uri('hasOutput'),
        'timeseries_output_ids':  PREFIX.SERVICES.alias_uri('hasOutput'),
        'parameters': PREFIX.SERVICES.alias_uri('parameters'),
        #
    }

    # Check references exist
    REFERENCES = {
        'service_id': PREFIX.SERVICES.alias_uri('Service'),
        'event_output_ids': [PREFIX.SERVICES.alias_uri('Event')],
        'timeseries_output_ids': [PREFIX.SERVICES.alias_uri('TimeSeries')],
        # 'parameters': [PREFIX.SERVICES.alias_uri('Parameter')],
    }

    FIELD_TO_REL_CPLX = {
        'service_id':
            '''?URI {rel} ?service. ?service {rel_id} ?service_id.\n'''.format(
                rel=LINKS['service_id'],
                rel_id=PREFIX.SERVICES.alias_uri('id')),
        'event':
            '''OPTIONAL{{?URI {rel} ?event. ?event a {cls}}}.\n'''.format(
                rel=LINKS['event_output_ids'],
                cls=REFERENCES['event_output_ids'][0]),
        'timeseries':
            '''OPTIONAL{{?URI {rel} ?series. ?series a {cls}}}.\n'''.format(
                rel=LINKS['timeseries_output_ids'],
                cls=REFERENCES['timeseries_output_ids'][0]),
    }

    SCHEMA = ModelSchema

    def _str_select(self, field, optional=False, dict_=None):
        """Build select line

        :param str field: Field name
        :param bool optional: Whether the field is optional (defaults to False)
        """
        dico = dict_ or self.FIELD_TO_RELATION
        return self._build_select_line(field, dico[field], optional=optional)

    def _build_filter(self, identifier, **filters):
        '''Build a string to add filtering parameters to a SPARQL query
        :param filters dict: a dictionary of parameter names, values
        :return a string to be inserted in the query'''
        filters_by_value = {k: filters[k] for k in self.FIELD_TO_RELATION
                            if k in filters}
        if 'service_id' in filters:
            filters_by_value['service_id'] = filters['service_id']
        if identifier:
            filters_by_value['id'] = str(identifier)
        return str_filter(filters_by_value)

    def _build_select_query(self, identifier=None, **filters):
        """A method to build the select query
        :return string: a string for the SPARQL query"""
        _select = [
            """SELECT ?URI
            (GROUP_CONCAT(?event; separator=',') as ?event_output_ids)
            (GROUP_CONCAT(?series; separator=',') as ?timeseries_output_ids)
            """] +\
            list(self.FIELD_TO_RELATION.keys()) + ['service_id']
        select = ' ?'.join(_select)
        query = ["""{sel} WHERE {{
                           ?URI a {clss}.
                """.format(sel=select,
                           clss=PREFIX.SERVICES.alias_uri('Model'),)]
        query.append(self._str_select("id"))
        query.append(self._str_select("description", optional=True))
        query.append(self._str_select("name"))
        # get references
        for item in self.FIELD_TO_REL_CPLX:
            query.append(self.FIELD_TO_REL_CPLX[item])
        # add filters
        query.append(self._build_filter(identifier, **filters))
        query.append("}}\ngroup by ?URI ?{}".format(" ?".join(
            list(self.FIELD_TO_RELATION.keys()) + ['service_id'])))
        return "".join(query)

    def _pre_load_binding(self, binding):
        # outputs
        for tag in ['event_output_ids', 'timeseries_output_ids']:
            outputs = list(map(
                PREFIX.get_name,
                filter(lambda x: x != '',
                       binding.pop(tag, '').split(','))))
            binding[tag] = outputs
        # parameters
        binding['parameters'] = self._get_all_parameters(binding['id'])

    def _post_get(self, values):
        return (r for r in values if 'id' in r)

    def _get_all_parameters(self, model_id):
        """Retrieves all the parameters of a model as a dictionary.
        :param  model_id string: the unique identifier of the model.
        """
        query = """SELECT ?name ?value WHERE {{
                    {model} {rel} ?param.
                    ?param {rel_name} ?name;
                           {rel_val} ?value
                }}""".format(model=PREFIX.ROOT.alias_uri(model_id),
                             rel=self.LINKS['parameters'],
                             rel_name=PREFIX.SERVICES.alias_uri('param_name'),
                             rel_val=PREFIX.SERVICES.alias_uri('param_value'),)
        result = self.onto_mgr.perform(SPARQLOP.SELECT, query)
        return result.values

# ------------INSERTION

    def _build_create_query(self, _id, element):
        _class = PREFIX.SERVICES.alias_uri('Model')
        # Build the query
        query = """{{{0} a {1}; {2} "{3}" ;""".format(
            PREFIX.ROOT.alias_uri(_id), _class,
            self.FIELD_TO_RELATION['id'], _id)
        query += self._str_insert(element, "name")
        query += self._str_insert(element, "description", optional=True)
        query += "{rel} {obj}.".format(
            rel=self.LINKS['service_id'],
            obj=PREFIX.ROOT.alias_uri(element.service_id))
        query += "}"
        return query

    def create(self, element):
        _id = super().create(element)
        # Add outputs if necessary
        self._create_outputs(element.event_output_ids, _id)
        self._create_outputs(element.timeseries_output_ids, _id)
        self._create_parameters(element.parameters, _id)
        return _id

    def _create_outputs(self, outputs, _id):
        """Create all triples to describe the outputs associated to the model
        :param outputs List of Output objects
        :param _id String: the identifier of the element to which outputs are
        bound"""
        output_handler = OutputDB()
        output_id = [output_handler.create(output) for output in outputs]
        if output_id:
            query = "INSERT DATA {{{subj} {rel} {obj}.}}".format(
                subj=PREFIX.ROOT.alias_uri(_id),
                rel=PREFIX.SERVICES.alias_uri('usesModel'),
                obj=('; {} '.format(
                    PREFIX.SERVICES.alias_uri('usesModel')).join(output_id)))
            self.onto_mgr.perform(SPARQLOP.INSERT, query)

    def _create_parameters(self, params, _id):
        """Creates parameters in the data model based on the dictionnary passed
        as in the method.

        :param params Dictionary: pairs of name:value
        :returns List of ID"""
        pattern = """{id} a {clss}; {name} "{v_name}"; {val} {v_val}.
            {model_id} {rel} {id}.\n"""
        id_ = (generate_id() for l in range(len(params)))
        id_iter = iter(id_)
        lcore = [pattern.format(
            id=PREFIX.ROOT.alias_uri(id_iter.__next__()),
            clss=PREFIX.SERVICES.alias_uri('Parameter'),
            name=PREFIX.SERVICES.alias_uri('param_name'), v_name=param.name,
            val=PREFIX.SERVICES.alias_uri('param_value'), v_val=param.value,
            model_id=PREFIX.ROOT.alias_uri(_id), rel=self.LINKS['parameters'])
                 for param in params]
        self.onto_mgr.perform(
            SPARQLOP.INSERT, "INSERT DATA {{{}}}".format("".join(lcore)))

    def _str_insert(self, obj, attr, optional=False, final=False):
        """Build up the line corresponding to an object attribute, into
        a SPARQL insert method, in the form "relation value". Value is
        extracted from obj.attr, the relation is extracted from a dictionary.

        :subj String: the subject of the triple to be created
        :obj Object: an object
        :attr String: the name of the attribute
        :optional boolean: True if the element to be inserted is optional
        :return: a String to be inserted into the INSERT query, of the form
            rel value
        """
        dict_ = self.FIELD_TO_RELATION
        return str_insert(dict_, obj, attr, optional=optional, final=final)

    def _get_delete_for_update(self, uri):
        """Build the delete query. This method is specific to every object.

        :param uri string: the URI of the object to be removed.
        :return string, string: a SPARQL DELETE clause, and WHERE clause
        """
        self._remove_parameter(uri)
        to_remove = list(self.FIELD_TO_RELATION.values())
        # to_remove.extend([self.LINKS['localization'], self.LINKS['system']])
        return self._build_remove(uri, to_remove)

    def _remove_parameter(self, uri):
        """Removes all the parameters associated to a modele"""
        query = ("DELETE {{?s ?p ?v. {model} {rel} ?s.}} "
                 "WHERE {{{model} {rel} ?s.}}").format(
                     model=uri, rel=self.LINKS['parameters'])
        self.onto_mgr.perform(SPARQLOP.DELETE, query)

    def update(self, identifier, new_element):
        super().update(identifier, new_element)
        self._create_parameters(new_element.parameters, identifier)

    def remove(self, identifier):
        self._remove_parameter(PREFIX.ROOT.alias_uri(identifier))
        super().remove(identifier)
