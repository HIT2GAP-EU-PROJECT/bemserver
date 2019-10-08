"""Api IFC module views"""

from flask import send_from_directory
from flask.views import MethodView
from werkzeug.utils import secure_filename

from . import bp as api
from .schemas import (
    IFCFileSchemaView, IFCFileImportSchemaView,
    IFCFileQueryArgsSchema, IFCFileRequestBodySchema,
    IFCFileEtagSchema)
from . import filestorage as fsio
from .exceptions import IFCFileBadArchiveError, IFCFileImportError

from ...extensions.rest_api import abort, Page, check_etag, set_etag
from ...extensions.rest_api.doc_responses import build_responses
from ...extensions.database import db_accessor
from ...extensions.auth import auth_required

from ....models import IFCFile
from ....basicservices.bim.ifc_import import IfcImport


@api.route('/')
class IFCFiles(MethodView):
    """IFC file resources endpoint"""

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='List IFC files',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.arguments(IFCFileQueryArgsSchema, location='query')
    @api.response(
        IFCFileSchemaView(many=True), etag_schema=IFCFileEtagSchema(many=True))
    @api.paginate(Page)
    def get(self, args):
        """Return IFC file list"""
        # retrieve sort parameter
        sort = args.pop('sort', None)
        return db_accessor.get_list(IFCFile, args, sort)

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Upload a new IFC file',
        consumes=('multipart/form-data', ),
        produces=('application/json', ),
        responses=build_responses([201, 413, 422, 500])
    )
    @api.arguments(IFCFileRequestBodySchema, location='form')
    @api.response(IFCFileSchemaView, code=201, etag_schema=IFCFileEtagSchema)
    def post(self, new_data):
        """Upload a new IFC file"""
        # TODO: on any error, rollback actions
        # process fileinfo
        fileinfo = new_data.pop('fileinfo', None)
        if fileinfo is not None:
            filename = fileinfo.filename
            new_data['file_name'] = secure_filename(filename)
            new_data['original_file_name'] = filename

        # Save and return new item in DB
        item = IFCFile(**new_data)
        db_accessor.create(item)

        # save file data stream on disk
        fs_mgr = fsio.get_filestorage_manager()
        fs_entry = fs_mgr.add(item.id, item.file_name, fileinfo.stream)
        # a compressed archive can only contain one IFC file
        if fs_entry.is_compressed():
            extracted_file_paths = fs_entry.extract()
            if len(extracted_file_paths) != 1:
                raise IFCFileBadArchiveError()

        set_etag(item)

        return item


@api.route('/<uuid:file_id>')
class IFCFilesById(MethodView):
    """IFC file resource endpoint"""

    def _get_item(self, file_id):
        """Get an item from its ID"""
        return db_accessor.get_item_by_id(IFCFile, file_id)

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Get IFC file by ID',
        responses=build_responses([200, 404, 422, 500])
    )
    @api.response(IFCFileSchemaView, etag_schema=IFCFileEtagSchema)
    def get(self, file_id):
        """Return an item from its ID"""
        item = self._get_item(file_id)
        set_etag(item)
        return item

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Delete an IFC file',
        responses=build_responses([204, 404, 422, 500])
    )
    @api.response(code=204, etag_schema=IFCFileEtagSchema)
    def delete(self, file_id):
        """Delete an item from its ID"""
        item = self._get_item(file_id)
        check_etag(item)
        try:
            fs_mgr = fsio.get_filestorage_manager()
            fs_mgr.delete(item.id)
        except FileNotFoundError as exc:
            abort(404, exc=exc)
        db_accessor.delete(item)


@api.route('/<uuid:file_id>/import')
class IFCFilesByIdImport(MethodView):
    """IFC file import endpoint."""

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Import an IFC file',
        responses=build_responses([201, 413, 422, 500])
    )
    @api.response(IFCFileImportSchemaView, code=201)
    def post(self, file_id):
        """Import an IFC file, found and loaded with its ID."""
        item = db_accessor.get_item_by_id(IFCFile, file_id)

        fs_mgr = fsio.get_filestorage_manager()
        try:
            fs_entry = fs_mgr.get(item.id)
        except FileNotFoundError as exc:
            abort(404, exc=exc)

        file_path = fs_entry.file_path
        # a compressed archive can only contain one IFC file
        if fs_entry.is_compressed():
            # archive should already be extracted
            file_path = fs_entry.extracted_file_paths[0]

        # import ifc file content in DB
        try:
            # TODO: as it takes time, this should be an asynchronous task...
            ifc_import = IfcImport(str(file_path))
            ifc_import.execute()
        except TypeError as exc:
            raise IFCFileImportError(str(exc))

        return {'success': True}


@api.route('/<uuid:file_id>/<string:file_name>')
class IFCFilesByIdDownload(MethodView):
    """IFC file download endpoint"""

    @auth_required(roles=['building_manager'])
    @api.doc(
        summary='Download IFC file',
        consumes=('application/json', ),
        produces=('application/octet-stream', ),
        responses=build_responses([200, 404, 422, 500])
    )
    def get(self, file_id, file_name):
        """Return an item from its ID"""
        item = db_accessor.get_item_by_id(IFCFile, file_id)

        if item.file_name != file_name:
            abort(404, message='Invalid file name.')

        fs_mgr = fsio.get_filestorage_manager()
        try:
            fs_entry = fs_mgr.get(file_id)
        except FileNotFoundError as exc:
            abort(404, exc=exc)

        return send_from_directory(
            str(fs_entry.file_path.parent), file_name), 200
