"""
Module for generating map with films locations.
"""
from math import radians,sin,cos,asin,sqrt
import folium
from geopy.exc import GeocoderUnavailable
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
def read_necessary_information(path,user_year):
    """
    Reads file and returns list of lists which have information about films.
    >>> read_necessary_information("locations","1890")
    [["London's Trafalgar Square ", '1890', "Trafalgar Square, St James's, London, England, UK"],\
 ['Monkeyshines, No. 1 ', '1890', 'Edison Laboratories, West Orange, New Jersey, USA'],\
 ['Monkeyshines, No. 2 ', '1890', 'Edison Laboratories, West Orange, New Jersey, USA'],\
 ['Monkeyshines, No. 3 ', '1890', 'Edison Laboratories, West Orange, New Jersey, USA']]
    """
    f_open = open(path, mode="r", encoding="UTF-8", errors='ignore')
    lines = []
    for line in f_open:
        if len(lines)<100:
            line = line.strip("\n")
            line = line.split("\t")
            year = line[0][(line[0].find("(") + 1):(line[0].find("(") + 5)]
            if year == user_year:
                place = line[-1]
                name = line[0][:line[0].find("(")]
                if place.startswith("("):
                    place = line[-2]
                if [name,year,place] not in lines:
                    lines.append([name,year,place])
    return lines


def locations_distance(lat_1,long_1,lat_2,long_2):
    """
    Returns distance between two coordinates.
    >>> locations_distance(47.6038321, -122.3300624, 48.287312, 25.1738)
    8978.763019742995
    >>> locations_distance(26.135, -123.98, 98.456, 100.309)
    6481.789297670148
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



def add_coordinates(films):
    """
    Returns information about film with coordinates of plece where it was filmed
    >>> add_coordinates(read_necessary_information("locations","1887"))
    []
    """
    geolocator = Nominatim(user_agent="user")
    for i,elem in enumerate(films):
        try:
            location = geolocator.geocode(elem[-1])
        except GeocoderUnavailable:
            elem[-1] = elem[-1].split(",")[0]
            location = geolocator.geocode(elem[-1])
        if location is not None:
            films[i].append((location.latitude,location.longitude))
        else:
            elem[-1] = elem[-1].strip(elem[-1].split(", ")[0])
            if elem[-1].startswith(", "):
                elem[-1] = elem[-1][2:]
            try:
                location = geolocator.geocode(elem[-1])
            except GeocoderUnavailable:
                continue
            if location is not None:
                films[i].append((location.latitude,location.longitude))
    return films


def find_ten_nearest(user_location, filtered_films_with_coordinates):
    """
    Returns information about ten nearest films which where filmed in specified year
    >>> find_ten_nearest((47.6038321, -122.3300624), add_coordinates(read_necessary_information\
("locations","1890")))
    [[7791.0368824231855, "London's Trafalgar Square ", (51.508037, -0.12804941070724718)],\
 [3885.883156517258, 'Monkeyshines, No. 1 ', (40.7987113, -74.2390353)], [3885.883156517258,\
 'Monkeyshines, No. 2 ', (40.7987113, -74.2390353)], [3885.883156517258, 'Monkeyshines, No. 3 ',\
 (40.7987113, -74.2390353)]]
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


def build_map(ten_nearest,users_location):
    """
    Builds maps with 3 layers: main layer, layer of ten nearest locations,
    distances from user`s location to the nearest locations.
    """
    film_map = folium.Map([users_location[0],users_location[1]])
    users_marker = folium.FeatureGroup(name="Your location")
    users_marker.add_child(folium.Marker(location=[users_location[0],users_location[1]],
                                         popup="Your location"))
    nearest_markers = folium.FeatureGroup(name="See 10 nearest locations of films")
    distances = folium.FeatureGroup(name="See distances")
    marker_cluster = MarkerCluster().add_to(nearest_markers)
    for i,elem in enumerate(ten_nearest):
        colors = ['darkpurple', 'blue', 'beige', 'orange', 'darkgreen', 'purple', 'pink',\
                  'lightgreen', 'green', 'darkblue']
        folium.Marker(location=[elem[-1][0], elem[-1][1]],
                      popup=elem[1],
                      icon=folium.Icon(color=colors[i])).add_to(marker_cluster)
        folium.PolyLine([[users_location[0],users_location[1]],[elem[-1][0], elem[-1][1]]],
                         popup="Distance:"+str(round(elem[0]))+" km.",
                         color=colors[i]).add_to(distances)
    film_map.add_child(nearest_markers)
    film_map.add_child(users_marker)
    film_map.add_child(distances)
    film_map.add_child(folium.LayerControl())
    film_map.save('films_map.html')

if __name__ == "__main__":
    input_year = input("Please enter a year you would like to have a map for: ")
    input_location = input("Please enter your location (format: lat, long): ")
    input_location = tuple(float(x) for x in input_location.split(", "))
    print("Map is generating...")
    build_map(find_ten_nearest((47.6038321, -122.3300624),\
              add_coordinates(read_necessary_information("locations",input_year))), input_location)
    print("Map is ready to use. Check films_map.html")
