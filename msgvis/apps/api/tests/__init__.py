def api_time_format(dt):
    """Convert a datetime to string according to the API settings"""
    from rest_framework.fields import DateTimeField

    field = DateTimeField()
    return field.to_representation(dt)

def django_time_format(dtstr):
    """Convert a datetime to string according to the API settings"""
    from rest_framework.fields import DateTimeField

    field = DateTimeField()
    return field.to_internal_value(dtstr)
