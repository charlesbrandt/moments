import sys, os
sys.path.append(os.path.dirname(os.getcwd()))

from moments.timestamp import *

def test_time():
    s = "*2008.10.22 11:15:42 suffix remainder here"
    (ts, remainder) = parse_line_for_time(s)
    assert ts == "*2008.10.22 11:15:42"

    t = Timestamp(tstamp=ts)
    t2 = datetime(2008, 10, 22, 11, 15, 42)
    assert t.datetime == t2

    t = Timestamp(tstamp="*2008.10.22 11:15")
    t2 = datetime(2008, 10, 22, 11, 15)
    assert t.datetime == t2

def test_this_week_last_year():
    now = datetime.now()
    year = timedelta(365)
    last_year = now - year
    start = last_year - timedelta(4)
    end = last_year + timedelta(4)

    stamp = start.strftime("%Y%m%d") + '-' + end.strftime("%Y%m%d")
    print this_week_last_year()
    assert stamp == this_week_last_year()

class TestTimestamp:
    def setUp(self):
        pass
    
    def test_init(self):
        #make sure it loads
        assert Timestamp("20090210")
        
class TestTimerange:
    def setUp(self):
        tstamp = "20081218210057"
        self.tr = Timerange(tstamp)

    def test_init(self):
        (start, end) = self.tr.as_tuple()
        t = datetime(2008, 12, 18, 21, 0, 57)
        assert start == t
        assert end == t

    def test_str(self):
        tstamp = "20081218"
        tr = Timerange(tstamp)
        print str(tr)
        assert str(tr) == "20081218-20081219"
        tstamp = "20081231"
        tr = Timerange(tstamp)
        assert str(tr) == "20081231-20090101"

    def test_from_trange(self):
        tstamp = "20081218"
        (start, end) = Timerange().from_trange(tstamp)
        #bit kludgy here... probably a better way to test for types
        assert str(type(start)) == "<type 'datetime.datetime'>"
        assert str(type(end)) == "<type 'datetime.datetime'>"
