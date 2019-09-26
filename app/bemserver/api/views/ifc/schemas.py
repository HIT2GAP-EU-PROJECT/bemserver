"""Api IFC module schemas"""

import marshmallow as ma

from ...extensions.rest_api import rest_api
from ...extensions.rest_api.query import SortQueryArgsSchema
from ...extensions.rest_api.hateoas import ma_hateoas
from ...extensions.rest_api.custom_fields import FileField

from ....models.ifc_file import IFCFile


class IFCFileSchema(ma.Schema):
    """IFC file schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    id = ma.fields.UUID(
        required=True,
        description='File ID'
    )
    description = ma.fields.String(
        validate=ma.validate.Length(max=250),
        description='File description'
    )

    original_file_name = ma.fields.String(
        required=True,
        description='Original file name'
    )
    file_name = ma.fields.String(
        required=True,
        description='File name (must be a `secured` file system name)'
    )

    @ma.validates_schema
    def validate_file_extension(self, data):
        """Return True if current file extension is approved."""
        allowed_extensions = IFCFile.ALLOWED_IFC_FILE_EXTENSIONS
        if len(allowed_extensions) > 0:
            for attr_name in ('file_name', 'original_file_name',):
                attr_val = data.get(attr_name, None)
                if (attr_val is not None and
                        not attr_val.lower().endswith(allowed_extensions)):
                    raise ma.ValidationError(
                        'Not a valid file extension. Allowed extensions: {}'
                        .format(allowed_extensions))


##########
# Schemas for API query parameters or request body/form

class IFCFileQueryArgsSchema(SortQueryArgsSchema):
    """IFCFile get query parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True

    original_file_name = ma.fields.String(
        description='Original file name'
    )
    file_name = ma.fields.String(
        description='File name'
    )


class IFCFileRequestBodySchema(IFCFileSchema):
    """IFCFile post/put request body parameters schema"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('id',)
        exclude = ('file_name', 'original_file_name',)

    fileinfo = FileField(
        required=True,
        location='files',
        load_from='file',
        # allowed_file_extensions is used in FileField validator
        allowed_file_extensions=IFCFile.ALLOWED_IFC_FILE_EXTENSIONS,
        description='Uploaded file informations'
    )


##########
# Schema for API responses

class IFCFileHateoasSchema(ma_hateoas.Schema):
    """IFCFile hateoas part schema for api views"""

    class Meta:
        """Schema Meta properties"""
        strict = True
        dump_only = ('_links',)

    _links = ma_hateoas.Hyperlinks(schema={
        'self': ma_hateoas.URLFor(endpoint='ifc.IFCFilesById', file_id='<id>'),
        'collection': ma_hateoas.URLFor(endpoint='ifc.IFCFiles'),
        'download': ma_hateoas.URLFor(
            endpoint='ifc.IFCFilesByIdDownload',
            file_id='<id>', file_name='<file_name>'),
    }, description='HATEOAS resource links')


@rest_api.definition('IFCFile')
class IFCFileSchemaView(IFCFileSchema, IFCFileHateoasSchema):
    """IFCFile schema for api views, with hateoas"""

    class Meta(IFCFileHateoasSchema.Meta):
        """Schema Meta properties"""
        strict = True
        dump_only = IFCFileHateoasSchema.Meta.dump_only + ('id',)


class IFCFileImportSchemaView(ma.Schema):
    """IFCFile schema for import result in api views."""

    class Meta:
        """Schema Meta properties."""
        strict = True
        dump_only = ('result',)

    success = ma.fields.Boolean(
        required=True,
        description='IFC file import result.',
    )


##########
# Schema for API etag feature

class IFCFileEtagSchema(IFCFileSchema):
    """IFCFile schema used by etag feature"""

    class Meta:
        """Schema Meta properties"""
        strict = True
