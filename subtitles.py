import re
import datetime
from pathlib import Path
from collections import namedtuple

Subline = namedtuple('Subline', ['start', 'end', 'text'])


def to_time(d):
    return datetime.time.fromisoformat(d.replace(',', '.'))


def parse_srt(srtfile):

    sub_number_reg = re.compile(r'^(\d+)\s*$')
    start_end_reg = re.compile(r'^(\d\d:\d\d:\d\d[,.]\d\d\d) --> (\d\d:\d\d:\d\d[,.]\d\d\d)\s*$')
    subs = []

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

        line_number = end_text_line_number + 1

    return subs
        


def test_parse():
    subs = parse_srt('test.srt')
    assert len(subs) == 11


if __name__ == '__main__':
    test_parse()
