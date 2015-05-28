def iso_8601(datetime):
    """Convert a datetime into an iso 8601 string."""
    if datetime is None:
        return datetime
    value = datetime.isoformat()
    if value.endswith('+00:00'):
        value = value[:-6] + 'Z'
    return value
