import unittest

from ais_tools import aivdm


class TestAIVDM(unittest.TestCase):
    def test_decode_message(self):
        line = '\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'
        actual = aivdm.decode_message(line)
        expected = {"tagblock_timestamp": 1577762601.537, "tagblock_station": "sdr-experiments",
                    "tagblock_T": "2019-12-30 22.23.21", "nmea": "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49",
                    "id": 1, "repeat_indicator": 0, "mmsi": 367596940, "nav_status": 0, "rot_over_range": True,
                    "rot": -731.386474609375, "sog": 0.0, "position_accuracy": 0, "x": -80.62191666666666,
                    "y": 28.408531666666665, "cog": 11.800000190734863, "true_heading": 511, "timestamp": 10,
                    "special_manoeuvre": 0, "spare": 0, "raim": False, "sync_state": 0, "slot_timeout": 5,
                    "received_stations": 29}
        self.assertDictEqual(actual, expected)
