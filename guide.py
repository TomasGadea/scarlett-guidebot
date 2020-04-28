import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, IconMarker
import pickle
import matplotlib.pyplot as plt


def download_graph(place):
    """ Downloads a graph from OpenStreetMap and returns it. Parameter is a string with the name of the location. """
    graph = ox.graph_from_place(
        place, network_type='drive', simplify=True)
    ox.geo_utils.add_edge_bearings(graph)
    return graph


def save_graph(graph, filename):
    """ Saves a graph (passed as first parameter) into a pickle file (named as second parameter). """
    f = open(filename, 'wb')
    pickle.dump(graph, f)
    f.close()


def load_graph(filename):
    """ Returns a graph read from a pickle file."""
    f = open(filename, 'rb')
    graph = pickle.load(f)
    f.close()
    return graph


def print_graph(graph):
    """ Represents graphicaly the graph passed as parameter and summarizes its information. """
    print(nx.info(graph))
    ox.plot_graph(graph)
    plt.show()


def get_directions(graph, source_location, destination_location):
    """ ... """
    pass


def plot_directions(graph, source_location, destination_location, directions,
                    filename, width=400, height=400):
    """ ... """
    pass
