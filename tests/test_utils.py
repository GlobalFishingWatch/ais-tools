import sys
import os
import unittest
import math
from datetime import datetime
from gpxpy.gpx import GPXTrackSegment
from gpxpy.gpx import GPXTrackPoint

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from generate_nmea import nmea_checksum
from generate_nmea import generate_gga
from generate_nmea import interpolate_line
from generate_nmea import interpolate_circle
from generate_nmea import KNOTS_TO_METERS_PER_SECOND


NMEA = [
    '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
    '!AIVDM,1,1,,B,15O0TWP1h0J>uK:@@MgCA9TD00Ru,0*32',
    '!AIVDM,2,1,7,A,55PH6Ml000000000000<OCGK;<0000000000000k10613t0002P00000,0*5E',
    '!AIVDM,2,2,7,A,000000000000000,2*23'
]


class TestGenerateNMEA(unittest.TestCase):
    def test_nmea_checksum(self):
        tests = [("$GPGGA,000000.00,4852.46626694,N,00217.58140440,E,1,05,2.87,+0.00,M,-21.3213,M,,*5E", 0x5e, 0x5e),
                 ("GPGGA,000000.00,4852.46626694,N,00217.58140440,E,1,05,2.87,+0.00,M,-21.3213,M,,", None, 0x5e),
                 ("$GPGGA,000000.00,4852.46626694,N,00217.58140440,E,1,05,2.87,+0.00,M,-21.3213,M,,", None, 0x5e)
                 ]

        for sentence, expected_checksum, expected_calc_checksum in tests:
            data, checksum, calc_checksum = nmea_checksum(sentence)
            assert (checksum == expected_checksum)
            assert (calc_checksum == expected_calc_checksum)

    def test_generate_gga(self):
        expected = "$GPGGA,010101.00,1230.00000000,N,09830.00000000,E,8,0,1.0,+100.00,M,0.0,M,,0000*7D"
        actual = generate_gga(datetime(2020, 1, 1, 1, 1, 1), 12.5, 98.5, 100.0)

        assert (actual == expected)

    def test_interpolate_line(self):
        p1 = GPXTrackPoint(0, 0)
        p2 = GPXTrackPoint(1, 0)
        start_time = datetime(2020, 1, 1, 0, 0, 0)
        speed_m = 60 * KNOTS_TO_METERS_PER_SECOND
        interval_s = 600
        # at 60 knots you go 60 NM or 1 degree in 1 hour
        points = list(interpolate_line(p1=p1, p2=p2, start_time=start_time, speed_m=speed_m, interval_s=interval_s))
        seg = GPXTrackSegment(points)
        assert (seg.get_points_no() == 7)
        assert (seg.get_duration() == 3600)
        assert (math.isclose(seg.length_2d(), 111000, rel_tol=0.01))

    def test_interpolate_circle(self):
        center_point = GPXTrackPoint(1, 1)
        radius_m = 500
        total_dist_m = 2 * math.pi * radius_m
        start_time = datetime(2020, 1, 1, 0, 0, 0)
        speed_m = math.pi * 10
        interval_s = 10
        points = interpolate_circle(center_point=center_point, radius_m=radius_m, total_dist_m=total_dist_m,
                                    start_time=start_time, speed_m=speed_m, interval_s=interval_s)
        seg = GPXTrackSegment(list(points))
        assert (seg.get_points_no() == 11)
        assert (seg.get_duration() == 100)
        assert (math.isclose(seg.length_2d(), total_dist_m, rel_tol=0.05))
