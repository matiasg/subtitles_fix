# subtitles_fix
tiny cli script to fix srt subtitles

So far it only shifts subtitles. Example:
```shell
➜ python subtitles.py -n 4 -t 01:23:45.678 test.srt test_output.srt

➜ head -n2 test_output.srt 
1
01:23:08,868 --> 01:23:14,942

➜ head -n2 test.srt 
1
00:00:06,000 --> 00:00:12,074

➜ grep -A1 '^4$' test_output.srt 
4
01:23:45,678 --> 01:23:48,014
```
