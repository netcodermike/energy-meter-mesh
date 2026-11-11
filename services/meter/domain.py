from datetime import datetime, timedelta

from errors import Rejected
from sqlite_store import transaction


def operation(data, _):
    site, readings = data["site"], data["readings"]
    if not isinstance(site, str) or not site.strip() or not isinstance(readings, list):
        raise ValueError("Expected site and readings")
    with transaction() as db:
        db.execute("CREATE TABLE IF NOT EXISTS reading (site TEXT, start TEXT, wh INTEGER, PRIMARY KEY (site, start))")
        for reading in readings:
            start = datetime.fromisoformat(reading["start"])
            wh = reading["wh"]
            if start.utcoffset() != timedelta(0) or start.minute % 30 or start.second or start.microsecond:
                raise ValueError("Expected an aligned half-hour UTC timestamp")
            if type(wh) is not int or not 0 <= wh <= 1_000_000_000:
                raise ValueError("Expected nonnegative integer watt-hours")
            key = site, start.isoformat()
            previous = db.execute("SELECT wh FROM reading WHERE site=? AND start=?", key).fetchone()
            if previous and previous[0] != wh:
                raise Rejected(409, "Reading already exists with a different value")
            db.execute("INSERT OR IGNORE INTO reading VALUES (?, ?, ?)", (*key, wh))
        rows = db.execute("SELECT start, wh FROM reading WHERE site=? ORDER BY start", (site,)).fetchall()
    return {"readings": [{"start": start, "wh": wh} for start, wh in rows]}
