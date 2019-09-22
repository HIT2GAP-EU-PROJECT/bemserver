"""API views schema base class"""

import math

import marshmallow as ma


class ObjectSchema(ma.Schema):
    """Schema to use as base Schema class for API views schema

    Provides method to instantiate or update objects.

    Subclass this schema and provide object class as Schema attritube:

    MyObject:
        [...]

    MyObjectSchema(ObjectSchema):
        _OBJ_CLS = MyObject
        [...]
    """

    class Meta:
        """Schema Meta properties"""
        strict = True

    # Override this with an Object class to deserialize as an object
    # in make_obj and update_obj
    # TODO: Make this abstract, see https://stackoverflow.com/a/23832581/
    # TODO: Or raise custom exception when calling getting attribute?
    _OBJ_CLS = None

    # TODO: do we need this method?
    def load_into_obj(self, data):
        """Load data and use it to instantiate an object

        :param dict data: Data to load

        Calls make_obj after deserializing data
        """
        return self.make_obj(self.load(data)[0])

    def make_obj(self, data):
        """Use deserialized data to instantiate an object

        :param dict data: Deserialized data used to instantiate object

        Works recursively with embedded objects.
        """
        for name, field in self.fields.items():
            key = field.attribute or name
            if key in data:
                if isinstance(field, ma.fields.Nested):
                    if field.many:
                        data[key] = [field.schema.make_obj(val)
                                     for val in data[key]]
                    else:
                        data[key] = field.schema.make_obj(data[key])
                elif (
                        isinstance(field, ma.fields.List) and
                        isinstance(field.container, ma.fields.Nested)):
                    data[key] = [field.container.schema.make_obj(val)
                                 for val in data[key]]

        return self._OBJ_CLS(**data)

    def _null_obj_attribute(self, obj, key, field):
        """Null attribute of an object

        Set attribute to null value. Depending on the type of the field, the
        null value can be None, [], {}...

        :param Object obj: Object to modify
        :param str key: Attribute to nullify
        :param Field field: Corresponding Schema field
        """
        if (isinstance(field, ma.fields.List) or
                (isinstance(field, ma.fields.Nested) and field.many)):
            setattr(obj, key, [])
        elif isinstance(field, ma.fields.Dict):
            setattr(obj, key, {})
        else:
            setattr(obj, key, None)

    def update_obj(self, obj, data):
        """Update an object with deserialized data provided as a dict.

        :param dict data: Deserialiazed data used to update object

        This method updates the object attributes corresponding to all fields
        in the Schema that are not excluded or read-only with values from data.

        The schema acts as a mask. It allows to override all the attributes
        that are meant to be overriden (exposed in an API through this schema),
        setting those that are missing from input data to None, leaving intact
        those that are not exposed.

        Note that this mask mechanism does not recurse to nested schemas.
        First level attributes are either overridden or deleted. They can't be
        partially updated.
        """
        for name, field in self.fields.items():
            if not field.dump_only:
                key = field.attribute or name
                if key in data:
                    if isinstance(field, ma.fields.Nested):
                        if field.many:
                            data[key] = [field.schema.make_obj(val)
                                         for val in data[key]]
                        else:
                            data[key] = field.schema.make_obj(data[key])
                    elif (
                            isinstance(field, ma.fields.List) and
                            isinstance(field.container, ma.fields.Nested)):
                        data[key] = [field.container.schema.make_obj(val)
                                     for val in data[key]]
                    setattr(obj, key, data[key])
                else:
                    self._null_obj_attribute(obj, key, field)

    @ma.post_dump
    def remove_none_values(self, data):
        # TODO: Find a better way to remove null values
        # https://github.com/marshmallow-code/marshmallow/issues/229
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ErrorSchema(ma.Schema):
    """Error schema."""
    class Meta:
        """Schema Meta properties."""
        strict = True

    status = ma.fields.String(
        required=True,
        description='Error status code'
    )
    message = ma.fields.String(
        description='Error message'
    )
    errors = ma.fields.List(
        ma.fields.Raw(),
        description='Error details'
    )


# Monkey-patch Float to reject nan/infinity
class Float(ma.fields.Float):

    default_error_messages = {
        'special': 'Special numeric values are not permitted.',
    }

    def _format_num(self, value):
        if value is None:
            return None
        num = super()._format_num(value)
        if math.isnan(num) or num == math.inf or num == -math.inf:
            self.fail('special')
        return num


ma.fields.Float = Float
