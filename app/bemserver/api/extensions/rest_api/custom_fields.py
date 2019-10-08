"""Helper field to store `werkzeug.FileStorage` object

As example:
A file upload is processed with a 'multipart/form-data' POST request and we
want to retrieve the data of the file sent. FileField do the job!
"""

from werkzeug.datastructures import FileStorage
import marshmallow as ma


class FileValidator(ma.validate.Validator):
    """Validate a file extension.
    :param list approved_file_extensions: Extensions check list to allow file.
    :param str error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}`.
    """

    default_message = 'Not a valid file extension. Allowed: {allowed}'
    default_allowed_extensions = ()

    def __init__(self, allowed_file_extensions=None, error=None):
        self.allowed_file_extensions = (
            allowed_file_extensions or self.default_allowed_extensions)
        self.error = error or self.default_message

    def _repr_args(self):
        return 'allowed_file_extensions={}'.format(
            self.allowed_file_extensions)

    def _format_error(self, value, allowed_file_extensions):
        return self.error.format(input=value, allowed=allowed_file_extensions)

    def __call__(self, value):
        message = self._format_error(value, self.allowed_file_extensions)
        if not isinstance(value, FileStorage):
            raise ma.ValidationError(message)

        if len(self.allowed_file_extensions) > 0:
            filename = value.filename.lower()
            if not filename.endswith(self.allowed_file_extensions):
                raise ma.ValidationError(message)

        return value


class FileField(ma.fields.ValidatedField):
    """A file field."""

    default_error_messages = {
        'invalid': 'Not a valid file extension. Allowed: {allowed}'}

    def __init__(self, allowed_file_extensions=None, **kwargs):
        super(FileField, self).__init__(**kwargs)
        self.allowed_file_extensions = allowed_file_extensions
        # Insert validation into self.validators, many errors can be stored.
        self.validators.insert(0, FileValidator(
            allowed_file_extensions=self.allowed_file_extensions,
            error=self.error_messages['invalid']
        ))

    def _validated(self, value):
        if value is None:
            return None
        return FileValidator(
            allowed_file_extensions=self.allowed_file_extensions,
            error=self.error_messages['invalid']
        )(value)
