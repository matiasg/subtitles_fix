from datetime import timedelta
from pathlib import Path

import tempfile
from subtitles import parse_srt, output_srt, shift, shift_subline, Subline


def test_parse():
    subs = parse_srt('test.srt')
    assert len(subs) == 11
    assert len(subs[0].text) == 2
    assert len(subs[1].text) == 1

    assert subs[0].text[0] == 'sub 1, line 1'
    assert subs[0].text[1] == 'sub 1, line 2'

    assert subs[4].start == timedelta(seconds=45, microseconds=512000)
    assert subs[4].end == timedelta(seconds=47, microseconds=234000)


def test_shift():
    subs = parse_srt('test.srt')
    diff = timedelta(seconds=3)
    new_subs = shift(subs, diff)
    # manual check
    assert new_subs[4].start == timedelta(seconds=48, microseconds=512000)
    assert new_subs[4].end == timedelta(seconds=50, microseconds=234000)
    # whole checks
    for s, ns in zip(subs, new_subs):
        assert ns.text == s.text
        assert ns.start == s.start + diff
        assert ns.end == s.end + diff


def test_shift_subline():
    subs = parse_srt('test.srt')
    new_time = timedelta(seconds=3)
    new_subs = shift_subline(subs, 5, new_time)
    assert new_subs[4].start == new_time
    assert new_subs[4].end == timedelta(seconds=4, microseconds=722000)


def test_output():
    subs = parse_srt('test.srt')

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        outfile = Path(tmpdir) / 'test_output.srt'

        output_srt(subs, str(outfile))
        assert Path(outfile).exists()

        new_subs = parse_srt(str(outfile))
        assert new_subs == subs


def test_output_with_negative_times():
    subs = parse_srt('test.srt')
    shifted_subs = shift(subs, timedelta(seconds=-20))

    with tempfile.TemporaryDirectory() as tmpdir:
        outfile = Path(tmpdir) / 'test_negative_time.srt'

        output_srt(shifted_subs, str(outfile))
        read_subs = parse_srt(str(outfile))

        assert len(read_subs) == len(shifted_subs) - 1
