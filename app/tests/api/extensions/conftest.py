"""Fixtures for api extensions tests"""

import pytest
import marshmallow as ma
from flask import Flask
from flask.views import MethodView

from flask_rest_api import Api, Blueprint, Page

from bemserver.api.extensions.rest_api.hateoas import ma_hateoas

from tests.api.utils import JSONResponse


class AppConfig():
    """Base application configuration class

    Overload this to add config parameters
    """


def create_app_mock(config_cls=None):
    """Return a basic API sample"""

    class AlbumSchema(ma.Schema):
        """Album resource schema"""
        class Meta:
            """Album schema Meta properties"""
            strict = True
        id = ma.fields.Integer()
        name = ma.fields.String()

        # Smart hyperlinking, hateoas style !
        _links = ma_hateoas.Hyperlinks(schema={
            'self': ma_hateoas.UrlFor(
                endpoint='albums.AlbumResourceById', album_id='<id>'),
            'collection': ma_hateoas.UrlFor(endpoint='albums.AlbumResources')
        })
        _embedded = ma_hateoas.Hyperlinks(schema={
            'songs': {
                '_links': {
                    'collection': ma_hateoas.UrlFor(
                        endpoint='songs.SongResources', album_id='<id>')
                }
            }
        })

    blp_albums = Blueprint('albums', __name__, url_prefix='/albums')

    @blp_albums.route('/')
    class AlbumResources(MethodView):
        """Album resources endpoints"""

        @blp_albums.arguments(AlbumSchema, location='query')
        @blp_albums.response(AlbumSchema(many=True))
        @blp_albums.paginate(Page)
        def get(self, args):
            """Return a list of resources"""
            album_datas = [
                {
                    'id': 0,
                    'name': 'Freak Out!'
                },
                {
                    'id': 1,
                    'name': 'Absolutely Free'
                }]
            return album_datas

        @blp_albums.arguments(AlbumSchema)
        @blp_albums.response(AlbumSchema, code=201)
        def post(self, new_item):
            """Create and return a resource"""
            return new_item

    @blp_albums.route('/<int:album_id>')
    class AlbumResourceById(MethodView):
        """Album resource endpoints"""

        @blp_albums.response(AlbumSchema)
        def get(self, album_id):
            """Return a resource from its ID"""
            album_data = {
                'id': album_id,
                'name': 'Freak Out!'
            }
            return album_data

    class SongSchema(ma.Schema):
        """Song resource schema"""
        class Meta:
            """Song schema Meta properties"""
            strict = True
        id = ma.fields.Integer()
        name = ma.fields.String()
        album_id = ma.fields.Integer()

        # Smart hyperlinking, hateoas style !
        _links = ma_hateoas.Hyperlinks({
            'self': ma_hateoas.UrlFor(
                endpoint='songs.SongResourceById', song_id='<id>'),
            'collection': ma_hateoas.UrlFor(endpoint='songs.SongResources'),
            'parent': ma_hateoas.UrlFor(
                endpoint='albums.AlbumResourceById', album_id='<album_id>')
        })

    blp_songs = Blueprint('songs', __name__, url_prefix='/songs')

    @blp_songs.route('/')
    class SongResources(MethodView):
        """Song resources endpoints"""

        @blp_songs.arguments(SongSchema, location='query')
        @blp_songs.response(SongSchema(many=True))
        @blp_songs.paginate(Page)
        def get(self, args):
            """Return a list of resources"""
            song_datas = [
                {
                    'id': 0,
                    'name': 'Hungry Freaks Daddy',
                    'album_id': 0
                },
                {
                    'id': 1,
                    'name': 'I Ain\'t Got No Heart',
                    'album_id': 0
                }]
            return song_datas

        @blp_songs.arguments(SongSchema)
        @blp_songs.response(SongSchema, code=201)
        def post(self, new_item):
            """Create and return a resource"""
            return new_item

    @blp_songs.route('/<int:song_id>')
    class SongResourceById(MethodView):
        """Song resource endpoints"""

        @blp_songs.response(SongSchema)
        def get(self, song_id):
            """Return a resource from its ID"""
            song_data = {
                'id': song_id,
                'name': 'Hungry Freaks Daddy',
                'album_id': 0
            }
            return song_data

    app = Flask('API Test')
    app.response_class = JSONResponse
    if config_cls:
        app.config.from_object(config_cls)
    api = Api(app)
    api.register_blueprint(blp_albums)
    api.register_blueprint(blp_songs)

    return app


@pytest.fixture(params=[AppConfig])
def app_mock(request):
    """Create and return a mocked Flask app"""
    config_cls = request.param

    # Create app
    request.cls.app = create_app_mock(config_cls)

    # Launch test client
    request.cls.client = request.cls.app.test_client()

    # Pass config to test function
    request.cls.config = config_cls
