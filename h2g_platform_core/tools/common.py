"""Common tools"""


def check_list_instances(values, instance_type):
    """Verify that a list of `values` are all an instance of `instance_type`"""
    return (isinstance(values, list) and
            all(isinstance(val, instance_type) for val in values))
