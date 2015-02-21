def api_time_format(dt):
    """Convert a datetime to string according to the API settings"""
    from rest_framework.fields import DateTimeField

    field = DateTimeField()
    return field.to_representation(dt)
