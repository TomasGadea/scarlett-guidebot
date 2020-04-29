import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
import pickle
import matplotlib.pyplot as plt


def download_graph(place):
    """ Downloads a graph from OpenStreetMap and returns it. Parameter is a
        string with the name of the location. """
    graph = ox.graph_from_place(
        place, network_type='drive', simplify=True)
    ox.geo_utils.add_edge_bearings(graph)
    return graph


def save_graph(graph, filename):
    """ Saves a graph (passed as first parameter) into a pickle file (named as
        second parameter). """
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
    """ Represents graphicaly the graph passed as parameter and summarizes its
        information. """
    print(nx.info(graph))
    ox.plot_graph(graph)
    plt.show()


def get_directions(graph, source_location, destination_location):
    """ ... """

    # it's ony an structure
    src = closest_node_of(source_location)
    dst = closest_node_of(destination_location)
    graph.add_edge_from([(source_location, src), (dst, destination_location)])
    nx.graph.shortest_path(source_location, destination_location)
    #


def plot_directions(graph, source_location, destination_location, directions,
                    filename, width=400, height=400):
    """ Plots the route from source_location to destination_location described
        by directions in a file named filename.png """
    m = StaticMap(width, height)
    for tram in directions:
        src = (tram['src'][1], tram['src'][0])
        dst = (tram['mid'][1], tram['mid'][0])
        coordinates = [[src[0], src[1]], [dst[0], dst[1]]]

        if tram['current_name'] is None:
            if tram['next_name'] is not None:
                marker = CircleMarker(src, 'blue', 20)
                line = Line(coordinates, 'blue', 4)
            else:
                marker = CircleMarker(src, 'red', 10)
                line = Line(coordinates, 'blue', 4)
        else:
            marker = CircleMarker(src, 'red', 10)
            line = Line(coordinates, 'red', 4)

        m.add_marker(marker)
        m.add_line(line)

        if tram['dst'] is None:
            marker = CircleMarker(dst, 'blue', 20)
            m.add_marker(marker)

    image = m.render()
    image.save(filename + '.png')
