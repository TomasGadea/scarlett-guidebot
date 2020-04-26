import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, IconMarker


download_graph(place):
    """ ... """

save_graph(graph, filename):
    """ ... """

load_graph(filename):
    """ ... """

print_graph(graph):
    """ ... """

get_directions(graph, source_location, destination_location):
    """ ... """

plot_directions(graph, source_location, destination_location, directions,
                filename, width=400, height=400):
    """ ... """
