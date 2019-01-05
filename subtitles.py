import re
import datetime
from pathlib import Path
from collections import namedtuple

from typing import List

Subline = namedtuple('Subline', ['start', 'end', 'text'])


def to_time(d: str) -> datetime.timedelta:
    t = datetime.time.fromisoformat(d.replace(',', '.'))
    return datetime.timedelta(hours=t.hour,
                              minutes=t.minute,
                              seconds=t.second,
                              microseconds=t.microsecond)


def parse_srt(srtfile: str) -> List[Subline]:
    sub_number_reg = re.compile(r'^(\d+)\s*$')
    start_end_reg = re.compile(r'^(\d\d:\d\d:\d\d[,.]\d\d\d) --> (\d\d:\d\d:\d\d[,.]\d\d\d)\s*$')
    subs: List[Subline] = []

    lines = Path(srtfile).read_text().splitlines()
    line_number = 0

    while line_number < len(lines):
        m = sub_number_reg.search(lines[line_number])
        assert m is not None
        sub_number = int(m.group(1))

        m = start_end_reg.search(lines[line_number + 1])
        assert m is not None
        start = to_time(m.group(1))
        end = to_time(m.group(2))

        try:
            end_text_line_number = lines.index('', line_number + 2)
        except ValueError:  # end of lines
            end_text_line_number = len(lines)
        text = lines[line_number + 2 : end_text_line_number]

        sub = Subline(start, end, text)
        subs.append(sub)
        assert sub_number == len(subs)  # consistency check

        line_number = end_text_line_number + 1

    return subs


def shift(subs: List[Subline], diff: datetime.timedelta) -> List[Subline]:
    newsubs = []
    for sub in subs:
        newsubs.append(Subline(sub.start + diff, sub.end + diff, sub.text))
    return newsubs



## tests
def test_parse():
    subs = parse_srt('test.srt')
    assert len(subs) == 11
    assert len(subs[0].text) == 2
    assert len(subs[1].text) == 1

    assert subs[0].text[0] == 'sub 1, line 1'
    assert subs[0].text[1] == 'sub 1, line 2'

    assert subs[4].start == datetime.timedelta(seconds=45, microseconds=512000)
    assert subs[4].end == datetime.timedelta(seconds=47, microseconds=234000)


def test_shift():
    subs = parse_srt('test.srt')
    subs = shift(subs, datetime.timedelta(seconds=3))

    assert subs[4].start == datetime.timedelta(seconds=48, microseconds=512000)
    assert subs[4].end == datetime.timedelta(seconds=50, microseconds=234000)


if __name__ == '__main__':
    test_parse()
