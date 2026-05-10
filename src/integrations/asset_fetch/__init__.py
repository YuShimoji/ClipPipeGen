"""Asset fetch integration boundary.

INT-02a starts with a fake source-audio generator. INT-02b fixes the boundary.
INT-02c adds local-media-audio FFmpeg normalization here only. yt-dlp, network
fetch, source-video fetch, and editing/rendering work remain outside this
package unless a later scoped slice explicitly adds them.
"""
