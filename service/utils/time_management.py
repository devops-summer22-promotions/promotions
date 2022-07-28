from datetime import date, datetime

def str_to_dt(date_string):
    """
    Converts date_string in Postgres format to a 3-tuple datetime for comparison in tests.
    """
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    year = dt.year
    month = dt.month
    day = dt.day
    return date(year, month, day)
