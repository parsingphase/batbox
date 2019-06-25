#!/usr/bin/env bash
for file in *.wav;do
    ident="${file%.*}"
    outfile="${file%.*}.png"
    sox "$file" -n spectrogram -o "$outfile" -t "$ident"
done

# from https://unix.stackexchange.com/questions/200168/how-to-create-the-spectrogram-of-many-audio-files-efficiently-with-sox?rq=1
# http://sox.sourceforge.net/sox.html
# Show file details:
#  soxi PIPPYG_20190624_213123.wav