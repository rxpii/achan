# achan
Dump 4chan thread images through a Discord bot

## Commands

`chn enable`: enable achan in the current channel (admin
only)

`chn disable`: disable achan in the current channel (admin
only)

`chn status`: check if achan is enabled in the current
channel (admin only)

`chn dump <board> <thread_id> [limit] [offset]`: dump the images of a
thread on a board. Optionally limit the number of dumped
images. Subsequent calls to this command will infer 
the offset of the next image to be dumped, if
offset is not manually supplied

`chn cont [limit] [offset]`: similar to `dump`, except the
board and thread id parameters are inferred from the
previous command
