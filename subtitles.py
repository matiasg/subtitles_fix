import re
import datetime
from pathlib import Path
from collections import namedtuple
from textwrap import dedent

from typing import List

class Subline(namedtuple('Subline', ['start', 'end', 'text'])):

    @staticmethod
    def format_datetime_time(t: datetime.timedelta) -> str:
        as_date = datetime.datetime(1, 1, 1) + t
        as_time = as_date.time()
        return f'{as_time.hour:02d}:{as_time.minute:02d}:{as_time.second:02d}.{as_time.microsecond // 1000:03d}'

    def format_time(self):
        return '{} --> {}'.format(self.format_datetime_time(self.start),
                                  self.format_datetime_time(self.end))

    def __str__(self):
        timeline = self.format_time()
        # textblock = '\n'.join(self.text)
        return '\n'.join((timeline, *self.text))

Subtitles = List[Subline]


def to_time(d: str) -> datetime.timedelta:
    t = datetime.time.fromisoformat(d.replace(',', '.'))
    return datetime.timedelta(hours=t.hour,
                              minutes=t.minute,
                              seconds=t.second,
                              microseconds=t.microsecond)


def parse_srt(srtfile: str) -> Subtitles:
    sub_number_reg = re.compile(r'^(\d+)\s*$')
    start_end_reg = re.compile(r'^(\d\d:\d\d:\d\d[,.]\d\d\d) --> (\d\d:\d\d:\d\d[,.]\d\d\d)\s*$')
    subs: Subtitles = []

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


def shift(subs: Subtitles, diff: datetime.timedelta) -> Subtitles:
    newsubs = []
    for sub in subs:
        newsubs.append(Subline(sub.start + diff, sub.end + diff, sub.text))
    return newsubs


def output_srt(subs: Subtitles, srtfile: str) -> None:
    with open(srtfile, 'w') as outfile:
        for sub_num, sub in enumerate(subs, start=1):
            print(sub_num, sub, '', sep='\n', file=outfile)


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
    diff = datetime.timedelta(seconds=3)
    new_subs = shift(subs, diff)
    # manual check
    assert new_subs[4].start == datetime.timedelta(seconds=48, microseconds=512000)
    assert new_subs[4].end == datetime.timedelta(seconds=50, microseconds=234000)
    # whole checks
    for s, ns in zip(subs, new_subs):
        assert ns.text == s.text
        assert ns.start == s.start + diff
        assert ns.end == s.end + diff

def test_output():
    subs = parse_srt('test.srt')

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        outfile = Path(tmpdir) / 'test_output.srt'

        output_srt(subs, str(outfile))
        assert Path(outfile).exists()

        new_subs = parse_srt(str(outfile))
        assert new_subs == subs
