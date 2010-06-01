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


class TestTimestamp:
    def setUp(self):
        pass
    
    def test_init(self):
        #make sure it loads
        assert Timestamp("20090210")

    def test_months(self):
        now = Timestamp()
        assert str(now.future_month(0)) == str(now.past_month(0))
        
class TestTimerange:
    def setUp(self):
        tstamp = "20081218210057"
        self.tr = Timerange(tstamp)

    def test_init(self):
        (start, end) = self.tr.as_tuple()
        t = datetime(2008, 12, 18, 21, 0, 57)
        assert start.datetime == t
        assert end.datetime == t

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
        assert str(type(start.datetime)) == "<type 'datetime.datetime'>"
        assert str(type(end.datetime)) == "<type 'datetime.datetime'>"

class TestRelativeRange:
    def setUp(self):
        tstamp = "20081218210057"
        self.tr = Timerange(tstamp)

        self.timerange = Timerange('20100428-20100528')

        self.rr = RelativeRange()
        self.dec = Timestamp(compact='201012')
        self.rr_dec = RelativeRange(self.dec)
        
    def test_year(self):
        assert str(self.rr.year()) == "20100101-20101231235959"

    def test_month(self):
        feb = Timestamp(compact='201002')
        dec_r = self.rr.month(self.dec)
        feb_r = self.rr.month(feb)
        assert str(dec_r) == "20101201-20101231235959"
        assert str(feb_r) == "20100201-20100228235959"

        nov_r = self.rr_dec.last_month()
        print nov_r
        assert str(nov_r) == "20101101-20101130235959"
        
        this_month_r = self.rr_dec.this_month()
        assert str(this_month_r) == "20101201-20101231235959"

        next_month_r = self.rr_dec.next_month()
        assert str(next_month_r) == "20110101-20110131235959"

    def test_week(self):
        week = self.rr.week()
        assert False


    ## def test_this_week_last_year():
    ##     now = datetime.now()
    ##     year = timedelta(365)
    ##     last_year = now - year
    ##     start = last_year - timedelta(4)
    ##     end = last_year + timedelta(4)

    ##     stamp = start.strftime("%Y%m%d") + '-' + end.strftime("%Y%m%d")
    ##     print this_week_last_year()
    ##     assert stamp == this_week_last_year()
