"""Module with utils class to handle the database interface"""

import uuid

from .ontology.exceptions import MissingValueError


def str_insert(dico, obj, attr, optional=False, prefix=None, final=False):
    """Build up the line corresponding to an object attribute, into
    a SPARQL insert method, in the form "relation value". Value is extracted
    from obj.attr, the relation is extracted from a dictionary.

    :param dico dictionary: the dictionary to be used
    :param obj Quantity
    :param attr String: the name of the attribute
    :param optional boolean: True if the element to be inserted is optional
    :param final boolean: True if it is a final insertion, i.e. ends with a dot
    :param stringify boolean: True if the element must be stringified
    :param return: a String to be inserted into the INSERT query, of the form
        rel value
    """
    try:
        val = getattr(obj, attr)
    except AttributeError:
        raise MissingValueError(
            'Missing attribute {} in object {}.'.format(attr, obj))
    if val is None:
        if not optional:
            raise MissingValueError(
                'No value provided for required attribute "{}" in {}.'
                .format(attr, obj))
        return ''
    if isinstance(val, str):
        val = '"{}" '.format(val) if not prefix else prefix.alias_uri(str(val))
    return ('{} {}.'.format(dico[attr], val) if final
            else '{} {};'.format(dico[attr], val))


def insert_line(relation, object_, subject=None, prefix=None, final=False,
                optional=True):
    """Add a line for insertion

    :param relation string: the relation to be added
    :param object string: the object of the triple to be added
    :param subject String: the subject of the triple - nothing if None
    :param prefix string: prefix of the object.
    :param final boolean: True if it is a final insertion, i.e. ends with a dot
    :param optional boolean: True if the element to be inserted is optional
    :param return: a String to be inserted into the INSERT query,
    """
    if optional and object_ is None:
        return ''
    if isinstance(object_, str):
        val = '"{}" '.format(object_) if not prefix\
            else prefix.alias_uri(str(object_))
    else:
        val = object_
    end = ('{} {}.'.format(relation, val) if final
           else '{} {};'.format(relation, val))
    return '{} {}'.format(subject or '', end)


def create_filter(name, value):
    '''Generate a line to filter a query. To be added in a SELECT query
    :param name string: the name if the filter. Must map a parameter of the
        querying
    :param value Object: values that must map the parameter name
    :return string: the filter line to be added in the query'''
    return 'FILTER (?{var} {op} {val}).'.format(var=name, op='=', val=value)


def str_filter(mapper, operation='='):
    '''Generate the FILTER line to be inserted into a query, according to the
    input dictionary
    :param mapper dictionary: a dictionary Name: Value
    :param operation string: the comparison operation
    :return string: a string to filter a SPARQL query'''
    str_ = ['{name} {op} {value}'.format(
        name='STR(?{})'.format(k), op=operation, value='"{}"'.format(
            mapper[k] if not isinstance(mapper[k], bool) else
            str(mapper[k]).lower()))
            for k in mapper]
    return 'FILTER({}).'.format(' && '.join(str_)) if str_ else ''


def str_filter_relation(map_id, map_relation, operation='EXISTS'):
    '''Generate the FILTER line to be inserted into a query, according to
    the input dictionary
    :param mapper dictionary: a dictionary Name: ID
    :param map_relation dictionary: a dictionary Name: partial query. The
        partial query should have a unique parameter named 'id'!!!!
    :param operation string: the operation to check the presence or absence of
        relation. Values can be EXISTS, or NOT EXISTS
    :return string: a string to filter a SPARQL query'''
    keys = set(map_id.keys()) & set(map_relation.keys())
    str_ = [map_relation[k].format(id=map_id[k]) for k in keys]
    return 'FILTER {} {{{}}}.'.format(operation, ' && '.join(str_)) \
        if str_ else ''


def generate_id():
    """Generate IDs. Should be called at each creation"""
    return uuid.uuid1()
