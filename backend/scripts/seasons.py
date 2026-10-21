import datetime


def get_current_season():
    """
    Get the current NBA season based on today's date.

    The NBA season is identified by the calendar year in which it ends:
    the 2025-26 season is returned as 2026, the 2026-27 season as 2027.

    Returns:
        int: Current season year
    """
    today = datetime.datetime.now()

    if today.month < 10:
        return today.year
    return today.year + 1
