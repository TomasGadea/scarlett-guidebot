import networkx as nx
import osmnx as ox
from haversine import haversine
from staticmap import StaticMap, Line, CircleMarker
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
    for node in directions:
        src = (node['src'][1], node['src'][0])
        dst = (node['mid'][1], node['mid'][0])
        coordinates = [[src[0], src[1]], [dst[0], dst[1]]]

        if node['current_name'] is None:
            if node['next_name'] is not None:
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

        if node['dst'] is None:
            marker = CircleMarker(dst, 'blue', 20)
            m.add_marker(marker)

    image = m.render()
    image.save(filename+'.png')


def main():
    print("downloading...")
    graph = download_graph("Berga, Spain")
    print("downloaded !")
    # print("saving...")
    # save_graph(hospi, "graf_hospi")
    # print("saved !")

    # hospi = load_graph("graf_hospi")
    # print_graph(bcn)
    # plot_directions(bcn, (41.40674136015038, 2.1738860390977446), (41.4034789, 2.1744103330097055), [{'angle': None, 'current_name': None, 'dst': (41.4061634, 2.1744054), 'length': None,'mid': (41.4070025, 2.1732822), 'next_name': 'Carrer de Lepant', 'src': (41.40674136015038, 2.1738860390977446)}, {'angle': 0.40200000000001523, 'current_name': 'Carrer de Lepant', 'dst': (41.4052928, 2.1755545), 'length': 132.215, 'mid': (41.4061634, 2.1744054), 'next_name': 'Carrer de Lepant', 'src': (41.4070025, 2.1732822)}, {'angle': 0.6809999999999832, 'current_name': 'Carrer de Lepant', 'dst': (41.4044287, 2.1766682),'length': 136.25400000000002, 'mid': (41.4052928, 2.1755545), 'next_name': 'Carrer de Lepant', 'src': (41.4061634, 2.1744054)}, {'angle': 88.957, 'current_name': 'Carrer de Lepant', 'dst': (41.4030085, 2.1747797), 'length': 133.644, 'mid': (41.4044287, 2.1766682), 'next_name': 'Carrer de Mallorca', 'src': (41.4052928, 2.1755545)}, {'angle': None, 'current_name': 'Carrer de Mallorca', 'dst': (41.4034789, 2.1744103330097055), 'length': 223.04499999999996, 'mid': (41.4030085, 2.1747797), 'next_name': None, 'src': (41.4044287, 2.1766682)}, {'angle': None, 'current_name': None, 'dst': None, 'length': None, 'mid': (41.4034789, 2.1744103330097055), 'next_name': None, 'src': (41.4030085, 2.1747797)}], "mapa_prova")

    # for each node and its information...
    for node1, info1 in graph.nodes.items():
        print(node1, info1)
        # for each adjacent node and its information...
        for node2, info2 in graph.adj[node1].items():
            print('    ', node2)
            # osmnx graphs are multigraphs, but we will just consider their first edge
            edge = info2[0]
            # we remove geometry information from edges because we don't need it and take a lot of space
            if 'geometry' in edge:
                del(edge['geometry'])
            print('        ', edge)


main()
