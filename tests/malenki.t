  $ [ "$0" != "/bin/bash" ] || shopt -s expand_aliases
  $ [ -n "$PYTHON" ] || PYTHON="`which python`"
  $ alias gpxsplitter="$PYTHON $TESTDIR/../gpxsplitter.py"

  $ cp $TESTDIR/malenki-20100130.gpx.gz $CRAMTMP
  $ cp $TESTDIR/malenki-20100130.gpx-out.tar.gz $CRAMTMP
  $ gzip -d $CRAMTMP/malenki-20100130.gpx.gz
  $ gpxsplitter $CRAMTMP/malenki-20100130.gpx
  Track from 2010-01-30 18:03:19+00:00 to 2010-01-30 18:03:19+00:00
  \twith 1 track points (esc)
  \tand 0 waypoints (esc)
  \twritten to 2010-01-30T18:03:19Z.gpx (esc)
  Track from 2010-01-30 18:06:42+00:00 to 2010-01-30 21:31:39+00:00
  \twith 11457 track points (esc)
  \tand 0 waypoints (esc)
  \twritten to 2010-01-30T21:31:39Z.gpx (esc)

  $ mkdir output
  $ mv *gpx output

Check last modified/accessed timestamps were set correctly

  $ stat --printf="%X %Y\n" output/*.gpx
  1264874599 1264874599
  1264887099 1264887099

Compare generated output with stored, correct output
  $ mkdir correct
  $ tar xzf $TESTDIR/malenki-20100130.gpx-out.tar.gz -C correct
  $ diff -uNr correct output
