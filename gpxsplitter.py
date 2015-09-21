#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

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
import time

import dateutil.parser

from lxml import etree

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
    # Detect whether GPX 1.0 or 1.1 is in use
    gpx_ns = document.xpath('namespace-uri(.)')
    gpx_namespaces = ['http://www.topografix.com/GPX/1/0',
                      'http://www.topografix.com/GPX/1/1']

    # FIXME: Turn this into an exception
    if gpx_ns not in gpx_namespaces:
        print >> sys.stderr, 'Unable to determine GPX version (neither 1.0 or 1.1)' % prog_name
        sys.exit(1)

    track_objects = []
    track_elements = document.findall('{%s}trk' % gpx_ns)
    for track_element in track_elements:
        document.getroot().remove(track_element)

        # Remove track numbering
        number = track_element.find('{%s}number' % gpx_ns)
        if number is not None:
            track_element.remove(number)

        points = track_element.findall('.//{%s}trkpt' % gpx_ns)
        bbox = determineBoundingBox(points)

        start_date = dateutil.parser.parse(points[0].find('{%s}time' % gpx_ns).text)
        end_date = dateutil.parser.parse(points[-1].find('{%s}time' % gpx_ns).text)

        track_obj = TrackTuple(
            track_etree=track_element, num_points=len(points),
            bounding_box=bbox,
            start_date=start_date, end_date=end_date,
            waypoints=[])
        track_objects.append(track_obj)

    waypoints = document.findall('//{%s}wpt' % gpx_ns)
    for waypoint in waypoints:
        wpt_time = dateutil.parser.parse(waypoint.find('{%s}time' % gpx_ns).text)
        document.getroot().remove(waypoint)

        # If waypoint was recording in a track's time interval, store
        for track in track_objects:
            if track.start_date <= wpt_time and wpt_time <= track.end_date:
                track.waypoints.append(waypoint)
                continue
            #print 'Waypoint %s could not be placed' % waypoint.find('{%s}name' % gpx_ns).text

    document_template = document

    for i, t in enumerate(track_objects):
        # Make a copy of the GPX file template for
        document = copy.deepcopy(document_template)

        filename = t.end_date.strftime('%Y-%m-%dT%H_%M_%SZ') + '.gpx'

        # Set metadata time to time of latest trackpoint
        metadata_tag = document.find('{%s}metadata' % gpx_ns)
        if metadata_tag is None:
            metadata_tag = etree.Element('{%s}metadata' % gpx_ns)
            document.getroot().append(metadata_tag)

        metadata_time_tag = metadata_tag.find('{%s}time' % gpx_ns)
        if metadata_time_tag is None:
            metadata_time_tag = etree.Element('{%s}time' % gpx_ns)
            metadata_tag.append(metadata_time_tag)
        metadata_time_tag.text = t.end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Set bounds based on trackpoints going into this file
        bounds_tag = metadata_tag.find('.//{%s}bounds' % gpx_ns)
        if bounds_tag is None:
            bounds_tag = etree.Element('{%s}bounds' % gpx_ns)
            metadata_tag.append(bounds_tag)
        for attrib_name in ('minlat', 'minlon', 'maxlat', 'maxlon'):
            bounds_tag.attrib[attrib_name] = t.bounding_box[attrib_name]

        # Add elements
        document.getroot().append(t.track_etree)
        document.getroot().extend(t.waypoints)

        print('Track from %s to %s\n\twith %d track points\n\tand %d waypoints\n\twritten to %s' \
          % (t.start_date, t.end_date, t.num_points, len(t.waypoints), filename))

        # Construct UNIX timestamp for output file
        f_time = time.mktime(t.end_date.timetuple())

        document.write(filename, pretty_print=True)
        os.utime(filename, (f_time, f_time))

    return


if __name__ == '__main__':
    import sys

    prog_name = os.path.basename(sys.argv[0])

    try:
        for ext in ['', '.gpx', '.GPX']:
            try:
                file_name = sys.argv[1] + ext
                document = etree.parse(file_name)
                break
            except IOError:
                print('Input file not found: %s' % file_name, file=sys.stderr)

        go(document)

    except (NameError, IndexError):
        print('Usage: %s filename.gpx' % prog_name, file=sys.stderr)
        sys.exit(1)
