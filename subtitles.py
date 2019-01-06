import re
import datetime
from pathlib import Path
from collections import namedtuple

from typing import List


class Subline(namedtuple('Subline', ['start', 'end', 'text'])):

    @staticmethod
    def format_datetime_time(t: datetime.timedelta) -> str:
        as_date = datetime.datetime(1, 1, 1) + t
        as_time = as_date.time()
        return (f'{as_time.hour:02d}:{as_time.minute:02d}:{as_time.second:02d}'
                f'.{as_time.microsecond // 1000:03d}')

    def format_time(self):
        return '{} --> {}'.format(self.format_datetime_time(self.start),
                                  self.format_datetime_time(self.end))

    def has_nonnegative_start(self):
        return self.start >= datetime.timedelta(0)

    def __str__(self):
        timeline = self.format_time()
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
    start_end_reg = re.compile(r'^(\d\d:\d\d:\d\d[,.]\d\d\d)'
                               r' --> (\d\d:\d\d:\d\d[,.]\d\d\d)\s*$')
    subs: Subtitles = []

    lines = Path(srtfile).read_text(encoding='latin1').splitlines()
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
        text = lines[line_number + 2:end_text_line_number]

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


def shift_subline(subs: Subtitles,
                  sub_number: int,
                  wanted_start: datetime.timedelta
                  ) -> Subtitles:
    sub = subs[sub_number - 1]
    diff = wanted_start - sub.start
    return shift(subs, diff)


def output_srt(subs: Subtitles, srtfile: str) -> None:
    sub_num = 1
    with open(srtfile, 'w', encoding='latin1') as outfile:

        for sub in subs:
            if sub.has_nonnegative_start():

                if sub_num > 1:
                    print('', file=outfile)

                print(sub_num, sub, sep='\n', file=outfile)
                sub_num += 1
