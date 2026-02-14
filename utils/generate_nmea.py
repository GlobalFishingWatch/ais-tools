import click

import copy
import operator
import math
from math import floor
from datetime import datetime, timedelta, timezone
from functools import reduce

from gpxpy.gpx import GPXTrackPoint
from gpxpy.geo import LocationDelta

KNOTS_TO_METERS_PER_SECOND = 0.514444


def nmea_checksum(sentence):
    """
    Compute the checksum for an NMEA sentence

    The sentence may optionally start with a "$" which is ignored and
    may or may not have  a checksum at the end separated by "*"

    The return is a tuple containing the data portion of the sentence which is used to compute the checksum,
    the value of the checksum, if any, that was passed at the end of the sentence and the
    checksum value that is calculated using the data portion of the sentence
    """
    sentence = sentence.strip().lstrip('$')

    parts = sentence.split('*', 1)
    parts = parts if len(parts) == 2 else (parts[0], None)
    data, checksum = parts
    checksum = int(checksum, 16) if checksum is not None else None

    calc_checksum = reduce(operator.xor, (ord(s) for s in data), 0)

    return data, checksum, calc_checksum


def generate_gga(time, latitude, longitude, elevation):
    """
    Generate a single GGA NMEA sentence
    """

    # Specify some default values for fields we don't care about
    num_sats = "0"
    hdop = "1.0"
    fix_type = "8"
    geoid_heght = "0.0"
    correction_data_age = ""
    station_id = "0000"

    time_format = '{:0>2}{:0>2}{:0>5.2f}'.format(time.hour, time.minute, time.second + time.microsecond/1000000)

    lat_abs = abs(latitude)
    lat_deg = floor(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60.0
    lat_format = '{:0>2.0f}{:0>11.8f}'.format(lat_deg, lat_min)
    lat_pole = "N" if latitude >= 0 else "S"

    lon_abs = abs(longitude)
    lon_deg = floor(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60
    lon_format = '{:0>3.0f}{:0>11.8f}'.format(lon_deg, lon_min)
    lon_pole = "E" if longitude >= 0 else "W"

    elevation_format = "{:+.2f}".format(elevation or 0.0)

    elements = ["GPGGA", time_format, lat_format, lat_pole, lon_format, lon_pole, fix_type,
                num_sats, hdop, elevation_format, "M", geoid_heght, "M", correction_data_age, station_id]
    sentence = ",".join(elements)
    checksum = nmea_checksum(sentence)[2]
    return "${}*{:02X}".format(sentence, checksum)


def gpx2nmea(p: "GPXTrackPoint"):
    """render a GPX point as a GGA NMEA string"""
    return generate_gga(time=p.time, latitude=p.latitude, longitude=p.longitude, elevation=p.elevation)


def interpolate_line(p1: "GPXTrackPoint", p2: "GPXTrackPoint",
                     start_time: "datetime", speed_m: "float",
                     interval_s: "float"):
    """
    interpolate points on a line from p1 to p2, moving at speed (meters/sec)
    with a position every interval seconds
    """
    total_distance = p1.distance_2d(p2)
    time_delta = timedelta(seconds=interval_s)
    dist_delta = speed_m * interval_s
    location_delta = LocationDelta(dist_delta, p1.course_between(p2))
    steps = int(round(total_distance / dist_delta))
    p = GPXTrackPoint(latitude=p1.latitude,
                      longitude=p1.longitude,
                      elevation=p1.elevation,
                      time=start_time,
                      speed=speed_m)
    for i in range(0, steps + 1):
        next_p = copy.deepcopy(p)
        next_p.move(location_delta)
        next_p.adjust_time(time_delta)
        yield p
        p = next_p


def interpolate_circle(center_point: "GPXTrackPoint", radius_m: "float", total_dist_m: "float",
                       start_time: "datetime", speed_m: "float", interval_s: "float"):
    """Interpolate points on a circular path.  Go around the circle repeatedly until total_dist_m is reached"""
    circumference = math.pi * radius_m * 2
    time_delta = timedelta(seconds=interval_s)
    dist_delta = speed_m * interval_s
    angle_delta = math.degrees(dist_delta / circumference * 2 * math.pi)

    angle = 0.0
    dist = 0.0
    time = start_time
    p = GPXTrackPoint(latitude=center_point.latitude,
                      longitude=center_point.longitude,
                      elevation=center_point.elevation,
                      time=start_time,
                      speed=speed_m)
    while dist <= total_dist_m:
        next_p = copy.deepcopy(p)
        next_p.move(LocationDelta(distance=radius_m, angle=angle))
        next_p.time = time
        yield next_p
        dist += dist_delta
        angle += angle_delta
        time += time_delta


@click.group()
def cli():
    pass


@cli.command()
@click.argument('lat1', type=click.FLOAT)
@click.argument('lon1', type=click.FLOAT)
@click.argument('lat2', type=click.FLOAT)
@click.argument('lon2', type=click.FLOAT)
@click.option('--speed-kn', '-s', type=click.FLOAT, default=10, show_default="10 knots")
@click.option('--interval_s', '-i', type=click.FLOAT, default=0.1, show_default="0.1 seconds")
@click.option('--start-time', '-t',
              type=click.DateTime(formats=['%H:%M:%S']),
              default=datetime.now(timezone.utc).strftime('%H:%M:%S'),
              show_default="now")
def line(lat1, lon1, lat2, lon2, speed_kn, interval_s, start_time):
    points = interpolate_line(
        p1=GPXTrackPoint(latitude=lat1, longitude=lon1),
        p2=GPXTrackPoint(latitude=lat2, longitude=lon2),
        start_time=start_time,
        speed_m=speed_kn * KNOTS_TO_METERS_PER_SECOND,
        interval_s=interval_s)
    for p in points:
        print(gpx2nmea(p))


@cli.command()
@click.argument('latitude', type=click.FLOAT)
@click.argument('longitude', type=click.FLOAT)
@click.option('--radius-m', '-r', type=click.FLOAT, default=100.0, show_default="100 meters")
@click.option('--total-dist-m', '-d', type=click.FLOAT, default=1000.0, show_default="1000 meters")
@click.option('--speed-kn', '-s', type=click.FLOAT, default=10, show_default="10 knots")
@click.option('--interval_s', '-i', type=click.FLOAT, default=0.1, show_default="0.1 seconds")
@click.option('--start-time', '-t',
              type=click.DateTime(formats=['%H:%M:%S']),
              default=datetime.now(timezone.utc).strftime('%H:%M:%S'),
              show_default="now")
def circle(latitude, longitude, radius_m, total_dist_m, speed_kn, start_time, interval_s):
    points = interpolate_circle(
        center_point=GPXTrackPoint(latitude=latitude, longitude=longitude),
        radius_m=radius_m,
        total_dist_m=total_dist_m,
        start_time=start_time,
        speed_m=speed_kn * KNOTS_TO_METERS_PER_SECOND,
        interval_s=interval_s)
    for p in points:
        print(gpx2nmea(p))


if __name__ == '__main__':
    cli()
