import unittest
import math
from datetime import datetime
from click.testing import CliRunner
from gpxpy.gpx import GPXTrackSegment
from gpxpy.gpx import GPXTrackPoint

from tagblock import tagblock
from tagblock import add_tagblock
from tagblock import format_tagblock_t
from tagblock import extract_nmea
from parse_ais import parse_message
from generate_nmea import nmea_checksum
from generate_nmea import generate_gga
from generate_nmea import interpolate_line
from generate_nmea import interpolate_circle
from generate_nmea import KNOTS_TO_METERS_PER_SECOND

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ais import stream as ais_stream

NMEA = [
    '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
    '!AIVDM,1,1,,B,15O0TWP1h0J>uK:@@MgCA9TD00Ru,0*32',
    '!AIVDM,2,1,7,A,55PH6Ml000000000000<OCGK;<0000000000000k10613t0002P00000,0*5E',
    '!AIVDM,2,2,7,A,000000000000000,2*23'
]


class TestTagblockCli(unittest.TestCase):

    def test_basic_cli(self):
        runner = CliRunner()
        result = runner.invoke(tagblock, input="\n".join(NMEA))
        self.assertFalse(result.exception)
        output = result.output.split('\n')[:-1]
        self.assertEqual(len(output), len(NMEA))
        for item_in, item_out in zip(NMEA, output):
            self.assertTrue(len(item_in) < len(item_out))
            self.assertTrue(item_out.endswith(item_in))

    # make sure that our sample nmea messages parse correctly
    def test_nmea(self):
        for sentence in NMEA:
            tagblock, nmea = ais_stream.parseTagBlock(sentence)
            self.assertEqual(sentence, nmea)
            self.assertTrue(ais_stream.checksum.isChecksumValid(nmea))

    def test_add_tagblock(self):
        station = 'station'
        for sentence in NMEA:
            tagblock, nmea = ais_stream.parseTagBlock(add_tagblock(sentence, station))
            self.assertTrue(ais_stream.checksum.isChecksumValid(nmea))
            self.assertEqual(station, tagblock['tagblock_station'])
            # self.assertEqual(tagblock, '')
            c = format_tagblock_t(datetime.fromtimestamp(tagblock['tagblock_timestamp']))
            self.assertEqual(c, tagblock['tagblock_T'])

    def test_extract_nmea(self):
        for sentence in NMEA:
            nmea = extract_nmea("extra {}text".format(sentence))
            assert nmea == sentence


class TestParseMessage(unittest.TestCase):
    def test_parse_message(self):
        line = '\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'
        actual = parse_message(line)
        expected = {"tagblock_timestamp": 1577762601.537, "tagblock_station": "sdr-experiments",
                    "tagblock_T": "2019-12-30 22.23.21", "nmea": "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49",
                    "id": 1, "repeat_indicator": 0, "mmsi": 367596940, "nav_status": 0, "rot_over_range": True,
                    "rot": -731.386474609375, "sog": 0.0, "position_accuracy": 0, "x": -80.62191666666666,
                    "y": 28.408531666666665, "cog": 11.800000190734863, "true_heading": 511, "timestamp": 10,
                    "special_manoeuvre": 0, "spare": 0, "raim": False, "sync_state": 0, "slot_timeout": 5,
                    "received_stations": 29}
        self.assertDictEqual(actual, expected)


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

    def test_generate_gga (self):
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


    def test_interpolate_circle (self):
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


if __name__ == '__main__':
    unittest.main()
