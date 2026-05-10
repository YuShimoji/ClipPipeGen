"""Asset fetch integration boundary.

INT-02a starts with a fake source-audio generator. INT-02b fixes the boundary:
real yt-dlp / ffmpeg wrappers belong here in later slices, and must not leak
into STT, Editing core, rendering, or GUI action code.
"""
