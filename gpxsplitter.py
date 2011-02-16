#!/usr/bin/env python
# -*-python-*-

#__package__   = 'gpxsplitter'
__version__   = '0.2'
__author__    = 'Samat K Jain <samat@samat.org>'
__url__       = 'http://wiki.samat.org/GpxSplitter'
__copyright__ = 'Copyright (c) 2010 Samat K Jain.'
__license__   = 'GPL v3'

import collections
import copy
import os
import pprint

from lxml import etree
from mx.DateTime.ISO import ParseDateTimeUTC

GPX_NS = 'http://www.topografix.com/GPX/1/1',

TrackTuple = collections.namedtuple(
    'TrackTuple',
    ['track_etree',
     'num_points',
     'bounding_box',
     'waypoints',
     'start_date',
     'end_date'
    ])


def determineBoundingBox(points):
    """Determine the bounding box of a set of points.
    """
    # This is slow. But works correctly.
    lats = [p.attrib['lat'] for p in points]
    lons = [p.attrib['lon'] for p in points]

    lats.sort()
    lons.sort()

    r = {}
    r['minlat'], r['maxlat'] = lats[0], lats[-1]

    # Because we things kept as strings, sort is lexical instead of
    # numeric. Negative numbers were sorted in reverse
    r['minlon'], r['maxlon'] = lons[-1], lons[0]

    return r


def go(document):
    track_objects = []
    track_elements = document.findall('{%s}trk' % GPX_NS)
    for track_element in track_elements:
        document.getroot().remove(track_element)

        # Remove track numbering
        number = track_element.find('{%s}number' % GPX_NS)
        if number is not None:
            track_element.remove(number)

        points = track_element.findall('.//{%s}trkpt' % GPX_NS)
        bbox = determineBoundingBox(points)

        start_date = ParseDateTimeUTC(points[0].find('{%s}time' % GPX_NS).text)
        end_date = ParseDateTimeUTC(points[-1].find('{%s}time' % GPX_NS).text)

        track_obj = TrackTuple(
            track_etree=track_element, num_points=len(points),
            bounding_box=bbox,
            start_date=start_date, end_date=end_date,
            waypoints=[])
        track_objects.append(track_obj)

    waypoints = document.findall('//{%s}wpt' % GPX_NS)
    for waypoint in waypoints:
        time = ParseDateTimeUTC(waypoint.find('{%s}time' % GPX_NS).text)
        document.getroot().remove(waypoint)

        # If waypoint was recording in a track's time interval, store
        for track in track_objects:
            if track.start_date <= time and time <= track.end_date:
                track.waypoints.append(waypoint)
                continue
            #print 'Waypoint %s could not be placed' % waypoint.find('{%s}name' % GPX_NS).text

    document_template = document

    for i, t in enumerate(track_objects):
        # Make a copy of the GPX file template for
        document = copy.deepcopy(document_template)

        filename = t.end_date.strftime('%Y-%m-%dT%H:%M:%SZ') + '.gpx'

        # Set metadata time to time of latest trackpoint
        metadata_tag = document.find('{%s}metadata' % GPX_NS)
        if metadata_tag is None:
            metadata_tag = etree.Element('{%s}metadata')
            document.getroot().append(metadata_tag)

        metadata_time_tag = metadata_tag.find('{%s}time' % GPX_NS)
        if metadata_time_tag is None:
            metadata_time_tag = etree.Element('{%s}time')
            metadata_tag.append(metadata_time_tag)
        metadata_time_tag.text = t.end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Set bounds based on trackpoints going into this file
        bounds_tag = metadata_tag.find('.//{%s}bounds' % GPX_NS)
        if bounds_tag is None:
            bounds_tag = etree.Element('{%s}bounds')
            metadata_tag.append(bounds_tag)
        for attrib_name in ('minlat', 'minlon', 'maxlat', 'maxlon'):
            bounds_tag.attrib[attrib_name] = t.bounding_box[attrib_name]

        # Add elements
        document.getroot().append(t.track_etree)
        document.getroot().extend(t.waypoints)

        print 'Track from %s to %s\n\twith %d track points\n\tand %d waypoints\n\twritten to %s' % (t.start_date, t.end_date, t.num_points, len(t.waypoints), filename)

        document.write(filename, pretty_print=True)
        os.utime(filename, (t.end_date.ticks(), t.end_date.ticks()))


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        prog_name = os.path.basename(sys.argv[0])
        print >> sys.stderr, 'Usage: %s filename.gpx' % prog_name
        sys.exit(1)

    document = etree.parse(sys.argv[1])
    go(document)
