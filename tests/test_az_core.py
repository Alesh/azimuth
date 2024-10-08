from datetime import datetime, date

from azimuth.core.models import CandleQueryParams
from azimuth.core.utils import normalize_date, start_to_timestamp, end_to_timestamp, to_timestamp


def test_start_end_to_timestamp():
    start = start_to_timestamp("2024-10-01")
    end = end_to_timestamp("2024-10-01")
    assert normalize_date(start).isoformat('T', 'milliseconds') == '2024-10-01T00:00:00.000'
    assert normalize_date(end).isoformat('T', 'milliseconds') == '2024-10-01T23:59:59.999'

    start_d = start_to_timestamp(date(2024, 10, 1))
    end_d = end_to_timestamp(date(2024, 10, 1))
    assert normalize_date(start_d).isoformat('T', 'milliseconds') == '2024-10-01T00:00:00.000'
    assert normalize_date(end_d).isoformat('T', 'milliseconds') == '2024-10-01T23:59:59.999'

    start_l = to_timestamp("2024-10-01 00:00:00")
    end_l = to_timestamp("2024-10-02 00:00:00") - 1
    assert normalize_date(start_l).isoformat('T', 'milliseconds') == '2024-10-01T00:00:00.000'
    assert normalize_date(end_l).isoformat('T', 'milliseconds') == '2024-10-01T23:59:59.999'

    start_dt = to_timestamp(datetime(2024, 10, 1))
    end_dt = to_timestamp(datetime(2024, 10, 2)) - 1
    assert normalize_date(start_dt).isoformat('T', 'milliseconds') == '2024-10-01T00:00:00.000'
    assert normalize_date(end_dt).isoformat('T', 'milliseconds') == '2024-10-01T23:59:59.999'

    assert start == start_d == start_l == start_dt
    assert end == end_d == end_l == end_dt

def test_candle_query_params():
    class _CandleQueryParams(CandleQueryParams):

        def make_url(self, base: str, **kwargs) -> str:
            pass

    qd = _CandleQueryParams(symbol='TEST', start_date="2024-10-01", end_date="2024-10-01")
    qdt = _CandleQueryParams(symbol='TEST', start_date="2024-10-01 00:00:00", end_date="2024-10-01 23:59:59.999")
    assert start_to_timestamp(qd.start_date) == to_timestamp(qdt.start_date)
    assert end_to_timestamp(qd.end_date) == to_timestamp(qdt.end_date)
    assert True