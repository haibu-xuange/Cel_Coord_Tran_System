# celestial_coords.py

import math

def hms_to_hours(h, m, s):
    return h + m/60 + s/3600

def hours_to_hms(hours):
    hours = hours % 24
    h = int(hours)
    remainder = (hours - h) * 60
    m = int(remainder)
    s = (remainder - m) * 60
    return h, m, s

def dms_to_deg(degrees, minutes, seconds, sign):
    return sign * (degrees + minutes/60 + seconds/3600)

def deg_to_dms(deg):
    sign = 1 if deg >= 0 else -1
    deg_abs = abs(deg)
    degrees = int(deg_abs)
    remainder = (deg_abs - degrees) * 60
    minutes = int(remainder)
    seconds = (remainder - minutes) * 60
    return degrees, minutes, seconds, sign

def spherical_to_cartesian(ra_hours, dec_deg, distance):
    ra_deg = ra_hours * 15
    ra_rad = math.radians(ra_deg)
    dec_rad = math.radians(dec_deg)
    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance * math.sin(dec_rad)
    return x, y, z

def cartesian_to_spherical(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    if r == 0:
        return (0, 0, 0)
    ra_rad = math.atan2(y, x)
    ra_deg = math.degrees(ra_rad) % 360
    ra_hours = ra_deg / 15 % 24
    dec_rad = math.asin(z / r)
    dec_deg = math.degrees(dec_rad)
    return ra_hours, dec_deg, r