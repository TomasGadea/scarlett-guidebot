import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, IconMarker
import pickle
import matplotlib.pyplot as plt


download_graph(place):
    """ ... """

save_graph(graph, filename):
    """ ... """

load_graph(filename):
    """ This function returns a graph read from a pickle file. """
    f = open('filename', 'rb')
    graph = pickle.load(f)
    f.close()
    return graph

print_graph(graph):
    """ This function draws graphicaly the graph graph. """
    nx.draw(graph, with_labels=True, font_weight='bold')

get_directions(graph, source_location, destination_location):
    """ ... """

plot_directions(graph, source_location, destination_location, directions,
                filename, width=400, height=400):
    """ ... """
