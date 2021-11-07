import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    today_year = dt.date.today().year
    return {"year": today_year}
