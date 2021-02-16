import folium
from math import radians,sin,cos,asin,sqrt
from geopy.exc import GeocoderUnavailable
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim

def read_file(path):
    """
    Reads file and returns list of lists which have information about films.
    """
    f_open = open(path, mode="r", encoding="UTF-8", errors='ignore')
    lines = []
    for line in f_open:
        line = line.strip("\n")
        line = line.split("\t")
        year = line[0][(line[0].find("(") + 1):(line[0].find("(") + 5)]
        place = line[-1]
        name = line[0]
        if place.startswith("("):
            place = line[-2]
        lines.append([name,year,place])
    return lines[:2000]


def locations_distance(lat_1,long_1,lat_2,long_2):
    """
    Returns distance between two coordinates.
    >>> locations_distance(47.6038321, -122.3300624, 48.287312, 25.1738)

    """
    lat_1 = radians(int(lat_1))
    long_1 = radians(int(long_1))
    lat_2 = radians(int(lat_2))
    long_2 = radians(int(long_2))
    dlong =  long_2 - long_1
    dlat = lat_2 - lat_1
    distance = 2 * asin(sqrt(sin(dlat/2)**2 + cos(lat_1) * cos(lat_2) * sin(dlong/2)**2))
    earth_radius = 6371
    return distance*earth_radius


def filter_by_year(data_list,year):
    """
    Returns list of lists which encompass information about film that were released in specified year.
    >>> filter_by_year(read_file("locations_test.lst"),'2010')
    """
    filtered_films = []
    for i in data_list:
        if i[1] == year:
            filtered_films.append(i)
    return filtered_films


def add_coordinates(filtered_films):
    """
    Returns information about film with coordinates of plece where it was filmed
    """
    geolocator = Nominatim(user_agent="user")
    for i,elem in enumerate(filtered_films):
        try:
            location = geolocator.geocode(elem[-1])
        except GeocoderUnavailable:
            elem[-1] = elem[-1].split(",")[0]
            location = geolocator.geocode(elem[-1])
        if location != None:
            filtered_films[i].append((location.latitude,location.longitude))
        else:
            elem[-1] = elem[-1].strip(elem[-1].split(", ")[0])
            if elem[-1].startswith(", "):
                elem[-1] = elem[-1][2:]
            try:
                location = geolocator.geocode(elem[-1])
            except GeocoderUnavailable:
                continue
            if location != None:
                filtered_films[i].append((location.latitude,location.longitude))
    return filtered_films
# print(find_coordinates(filter_by_year(read_file("locations_test.lst"),'2010')))

def ten_nearest(user_location, filtered_films_with_coordinates):
    """
    Returns information about ten nearest films which where filmed in specified year

    """
    nearest = []
    for i in filtered_films_with_coordinates:
        try:
            int(i[-1][0])
            int(i[-1][1])
            distance = locations_distance(i[-1][0], i[-1][1], user_location[0], user_location[1])
            if len(nearest)<10:
                nearest.append([distance,i[0],i[-1]])
            elif len(nearest) == 10:
                if max(nearest)[0] > distance:
                    nearest[nearest.index(max(nearest))][0]=distance
        except ValueError:
            continue
    return nearest
# print(ten_nearest((47.6038321, -122.3300624), add_coordinates(filter_by_year(read_file("locations_test.lst"),'2010'))))
import gmaps
def build_map(ten_nearest,users_location):
    map = folium.Map()
    nearest_markers = folium.FeatureGroup(name="10 nearest locations")
    marker_cluster = MarkerCluster().add_to(nearest_markers)
    for i,elem in enumerate(ten_nearest):
        colors = ['darkpurple', 'blue', 'beige', 'orange', 'darkgreen', 'purple', 'lightred', 'darkred', 'pink', 'lightgreen', 'green', 'darkblue', 'lightgray', 'cadetblue', 'lightblue']
        folium.Marker(location=[elem[-1][0], elem[-1][1]],
                      popup=elem[1],
                      icon=folium.Icon(color=colors[i])).add_to(marker_cluster)
    map.add_child(nearest_markers)
    # layer = gmaps.directions.Directions(users_location,ten_nearest[0][-1],mode="car")
    # map.add_child(layer)
    map.save('films_map.html')
print(build_map(ten_nearest((48.287312, 25.1738), add_coordinates(filter_by_year(read_file("locations"),'2001'))),(48.287312, 25.1738))
)


