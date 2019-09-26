"""Tests for API views schema base class"""

import marshmallow as ma

from bemserver.api.extensions.rest_api.schemas import ObjectSchema

from tests import TestCoreApi


class TestApiExtensionsSchemas(TestCoreApi):

    def test_objectschema(self):

        class MyEmbeddedObj:
            def __init__(self, f=None, f_m='79'):
                super().__init__()
                self.f = f
                self.f_m = f_m

        class MyObj:
            def __init__(self, f=None, f_m=79, f_do=42, f_ex=12,
                         f_lf=None, f_a=None,
                         e=None, e_l=None, l_e=None):
                super().__init__()
                self.f = f
                self.f_m = f_m
                self.f_do = f_do
                self.f_ex = f_ex
                self.f_lf = f_lf
                self.f_a = f_a
                self.e = e
                self.e_l = e_l
                self.l_e = l_e

        class MyEmbeddedObjSchema(ObjectSchema):

            _OBJ_CLS = MyEmbeddedObj

            f = ma.fields.String()
            f_m = ma.fields.String(missing='69')

        class MyObjSchema(ObjectSchema):

            _OBJ_CLS = MyObj

            f = ma.fields.Integer()
            f_m = ma.fields.Integer(missing=69)
            f_do = ma.fields.Integer(dump_only=True)
            f_lf = ma.fields.Integer(load_from='f_lff')
            f_aa = ma.fields.Integer(attribute='f_a')
            e_a = ma.fields.Nested(MyEmbeddedObjSchema, attribute='e')
            e_l = ma.fields.Nested(MyEmbeddedObjSchema, many=True)
            l_e = ma.fields.List(ma.fields.Nested(MyEmbeddedObjSchema))

        # TODO: We should also test ma.fields.Dict but we don't use it anyway
        # TODO: In practice, Nested(many=True) fields should have missing=list
        # so that the client is not surprised by the return value, but doing
        # this here would defeat the purpose of the update test (null -> []).

        # Test load_into_obj

        my_obj = MyObjSchema().load_into_obj({
            'f': 1, 'f_do': 3, 'f_ex': 4, 'f_lff': 5, 'f_aa': 6,
            'e_a': {'f': 'a'}, 'e_l': [{'f': 'la'}], 'l_e': [{'f': 'la'}]})

        assert type(my_obj) == MyObj
        assert my_obj.f == 1
        assert my_obj.f_m == 69
        assert my_obj.f_do == 42
        assert my_obj.f_lf == 5
        assert my_obj.f_a == 6
        assert my_obj.f_ex == 12

        e = my_obj.e
        assert type(e) == MyEmbeddedObj
        assert e.f == 'a'
        assert e.f_m == '69'

        e_l = my_obj.e_l
        assert type(e_l) == list
        assert len(e_l) == 1
        e_l_0 = e_l[0]
        assert e_l_0.f == 'la'
        assert e_l_0.f_m == '69'

        l_e = my_obj.l_e
        assert type(l_e) == list
        assert len(l_e) == 1
        l_e_0 = l_e[0]
        assert l_e_0.f == 'la'
        assert l_e_0.f_m == '69'

        # Test make_obj

        my_obj = MyObjSchema().make_obj({
            'f': 1, 'f_do': 3, 'f_ex': 4, 'f_lf': 5, 'f_a': 6,
            'e': {'f': 'a'},
            'e_l': [{'f': 'la'}],
            'l_e': [{'f': 'la'}],
        })

        assert type(my_obj) == MyObj
        assert my_obj.f == 1
        assert my_obj.f_m == 79
        assert my_obj.f_do == 3
        assert my_obj.f_lf == 5
        assert my_obj.f_a == 6
        assert my_obj.f_ex == 4

        e = my_obj.e
        assert type(e) == MyEmbeddedObj
        assert e.f == 'a'
        assert e.f_m == '79'

        e_l = my_obj.e_l
        assert type(e_l) == list
        assert len(e_l) == 1
        e_l_0 = e_l[0]
        assert e_l_0.f == 'la'
        assert e_l_0.f_m == '79'

        l_e = my_obj.l_e
        assert type(l_e) == list
        assert len(l_e) == 1
        l_e_0 = l_e[0]
        assert l_e_0.f == 'la'
        assert l_e_0.f_m == '79'

        my_obj = MyObjSchema().make_obj({
            'f': 1, 'f_do': 3, 'f_ex': 4, 'f_lf': 5, 'f_a': 6})

        assert type(my_obj) == MyObj
        assert my_obj.f == 1
        assert my_obj.f_m == 79
        assert my_obj.f_do == 3
        assert my_obj.f_lf == 5
        assert my_obj.f_a == 6
        assert my_obj.f_ex == 4

        assert my_obj.e is None
        assert my_obj.e_l is None

        # Test update_obj

        my_obj = MyObj()
        assert my_obj.f is None
        assert my_obj.f_m == 79

        MyObjSchema().update_obj(
            my_obj,
            {
                'f': 12, 'f_m': 69, 'f_a': 42,
                'e': {'f': 'a'},
                'e_l': [{'f': 'la'}],
                'l_e': [{'f': 'la'}],
            })

        assert my_obj.f == 12
        assert my_obj.f_m == 69
        assert my_obj.f_do == 42
        assert my_obj.f_a == 42
        e = my_obj.e
        assert isinstance(e, MyEmbeddedObj)
        assert e.f == 'a'
        e_l = my_obj.e_l
        assert len(e_l) == 1
        e = e_l[0]
        assert isinstance(e, MyEmbeddedObj)
        assert e.f == 'la'
        l_e = my_obj.l_e
        assert len(l_e) == 1
        e = l_e[0]
        assert isinstance(e, MyEmbeddedObj)
        assert e.f == 'la'

        MyObjSchema(exclude=['f', ]).update_obj(
            my_obj,
            {
                'f_m': 69, 'f_a': 42,
            })

        assert my_obj.f == 12
        assert my_obj.f_m == 69
        assert my_obj.f_do == 42
        assert my_obj.f_a == 42
        assert my_obj.e is None
        assert my_obj.e_l == []
        assert my_obj.l_e == []
