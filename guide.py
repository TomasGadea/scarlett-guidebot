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

    for node1, info1 in graph.nodes.items():
        for node2, info2 in graph.adj[node1].items():
            edge = info2[0]
            if 'geometry' in edge:
                del(edge['geometry'])

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

    for node1, info1 in graph.nodes.items():
        print(node1, info1)
        for node2, info2 in graph.adj[node1].items():
            print('    ', node2)
            edge = info2[0]
            print('        ', edge)

    ox.plot_graph(graph)
    plt.show()


def get_directions(graph, source_location, destination_location):
    """ Return a list of maps. Each map conatins info about the section of the path (see from_path_to_directions). """
    src = closest_node_to(graph, source_location)
    src_coord = (graph.nodes[src]['y'], graph.nodes[src]['x'])
    print(src_coord)
    dst = closest_node_to(graph, destination_location)
    dst_coord = (graph.nodes[dst]['y'], graph.nodes[dst]['x'])
    print(dst_coord)

    graph.add_edges_from([(source_location, src, {'length': haversine(source_location, src_coord, unit='m')}), (dst, destination_location, {'length': haversine(destination_location, dst_coord, unit='m')})])
    shortest_path = nx.shortest_path(graph, source_location,
                                     destination_location)
    route = from_path_to_directions(graph, shortest_path)
    return route

def closest_node_to(graph, source_location):
    """ Return the graph node nearest to some specified source_location: (lat, lng) """

    return ox.geo_utils.get_nearest_node(graph, source_location, method='haversine')


def from_path_to_directions(graph, shortest_path):
    """ ... """
    directions = ox.geo_utils.get_route_edge_attributes(graph, shortest_path)


    for index, node1 in enumerate(shortest_path):
        for node2, info2 in graph.adj[node1].items():
            if node2 == shortest_path[index+1]:
                edge = info2[0]
                dic = {'angle': edge['bearing'],
                       'current_name': ,
                       'dst': ,
                       'length': ,
                       'mid': ,
                       'next_name': ,
                       'src': }
                directions.append(dic)
    return directions


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
