import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import pickle


def download_graph(place):
    graph = ox.graph_from_place(
        place, network_type='drive', simplify=True)
    ox.geo_utils.add_edge_bearings(graph)
    return graph


def save_graph(graph, filename):
    f = open(filename, 'wb')
    pickle.dump(graph, f)
    f.close()


def main():
    mapa = download_graph("Berga, Spain")


main()
