  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias gpxsplitter="$PYTHON $TESTDIR/../gpxsplitter.py"

  $ gpxsplitter
  Usage: gpxsplitter filename.gpx

  $ gpxsplitter filename
  Input file not found: filename
  Input file not found: filename.gpx
  Input file not found: filename.GPX
  Usage: gpxsplitter filename.gpx

  $ cp $TESTDIR/malenki-20100130.gpx.gz $CRAMTMP
  $ gzip -d $CRAMTMP/malenki-20100130.gpx.gz
  $ gpxsplitter $CRAMTMP/malenki-20100130
  Input file not found: $CRAMPTMP/malenki-20100130
  Track from 2010-01-30 18:03:19+00:00 to 2010-01-30 18:03:19+00:00
  \twith 1 track points (esc)
  \tand 0 waypoints (esc)
  \twritten to 2010-01-30T18:03:19Z.gpx (esc)
  Track from 2010-01-30 18:06:42+00:00 to 2010-01-30 21:31:39+00:00
  \twith 11457 track points (esc)
  \tand 0 waypoints (esc)
  \twritten to 2010-01-30T21:31:39Z.gpx (esc)
