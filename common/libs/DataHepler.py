

import datetime

def getCurrentTime(frm = "%Y-%m-%d %H:%M:%S"):
    dt=datetime.datetime.now()
    return dt.strftime(frm)