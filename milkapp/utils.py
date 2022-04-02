from math import sin, cos, sqrt, atan2, radians


def calculate_distance(latitude_A,longitude_A,latitude_B,longitude_B):

    R = 6373.0

    lat1 = radians(latitude_A)
    lon1 = radians(longitude_A)
    lat2 = radians(latitude_B)
    lon2 = radians(longitude_B)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    print("Result:", distance)
    return distance