from flask import g
from dateutil.parser import parse

months = {
    'January': 'Ionawr',
    'February': 'Chwefror',
    'March': 'Mawrth',
    'April': 'Ebrill',
    'May': 'Mai',
    'June': 'Mehefin',
    'July': 'Gorffennaf',
    'August': 'Awst',
    'September': 'Medi',
    'October': 'Hydref',
    'November': 'Tachwedd',
    'December': 'Rhagfyr'
}


def format_date(date, translate=True):
    formatted_date_list = date.strftime('%d %B %Y').split(' ')
    if translate and g.locale == 'cy':
        formatted_date_list[1] = months[formatted_date_list[1]]
    return ' '.join(str(i) for i in formatted_date_list)


def format_long_date(date):
    day = parse(date).day
    split_date = date.split()
    split_date[1] = months[split_date[1]]

    if day == 1:
        day = f'{day}af'
    elif day == 2:
        day = f'{day}ail'
    elif day == 3 or day == 4:
        day = f'{day}ydd'
    elif day == 5 or day == 6:
        day = f'{day}ed'
    elif day in [7, 8, 9, 10, 12, 15, 18, 20]:
        day = f'{day}fed'
    elif day in [11, 13, 14, 16, 17, 19]:
        day = f'{day}eg'
    else:
        day = f'{day}ain'
    split_date[0] = day

    return ' '.join(split_date)
