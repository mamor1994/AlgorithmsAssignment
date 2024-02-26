import networkx as nx
import random
import matplotlib.pyplot as plt

def generate_random_graph(num_nodes, steiner_percentage, max_edge_weight):
    G = nx.Graph()
    G.add_nodes_from(range(1, num_nodes + 1))

    # Create Steiner nodes
    num_steiner_nodes = int(steiner_percentage * num_nodes)
    steiner_nodes = random.sample(list(G.nodes()), num_steiner_nodes)
    print("Steiner nodes selected:", steiner_nodes)

    # Attach Steiner nodes to the graph
    for node in G.nodes():
        if node in steiner_nodes:
            G.nodes[node]['steiner'] = True
        else:
            G.nodes[node]['steiner'] = False

    # Create random edges
    num_edges = random.randint(num_nodes - 1, num_nodes * (num_nodes - 1) // 2)

    for u in G.nodes():
        while G.degree(u) < 1:
            v = random.choice(list(G.nodes()))
            if v != u and G.degree(v) < 2:
                weight = random.randint(1, max_edge_weight)
                G.add_edge(u, v, weight=weight)

    while G.number_of_edges() < num_nodes - 1:
        is_connected = nx.is_connected(G)
        if not is_connected:
            u = random.choice(list(G.nodes()))
            v = random.choice(list(G.nodes()))
            if u != v and not nx.has_path(G, u, v):
                weight = random.randint(1, max_edge_weight)
                G.add_edge(u, v, weight=weight)

    # Connect nodes until reaching the desired number of edges
    while G.number_of_edges() < num_edges:
        u = random.choice(list(G.nodes()))
        v = random.choice(list(G.nodes()))
        if u != v and not G.has_edge(u, v):
            weight = random.randint(1, max_edge_weight)
            G.add_edge(u, v, weight=weight)

    return G


def find_steiner_tree(G):
    G1 = build_complete_graph(G)
    print("Complete Graph from original G (G1):", G1.edges(data=True))

    T1 = nx.minimum_spanning_tree(G1)
    print("Minimum Spanning Tree (T1):", T1.edges(data=True))

    Gs = build_subgraph(G, T1)
    print("Constructed Subgraph (Gs):", Gs.edges(data=True))

    Ts = nx.minimum_spanning_tree(Gs)
    print("Minimum Spanning Tree (Ts):", Ts.edges(data=True))

    TH = build_steiner_tree(G, Ts)
    print("Steiner Tree (TH):", TH.edges(data=True))
    return TH


def build_complete_graph(G):
    G1 = nx.Graph()

    steiner_nodes = [node for node in G.nodes() if G.nodes[node].get('steiner', False)]
    G1.add_nodes_from(steiner_nodes)

    for u in steiner_nodes:
        for v in steiner_nodes:
            if u != v:
                weight = nx.shortest_path_length(G, u, v, weight='weight')
                G1.add_edge(u, v, weight=weight)

    return G1


def build_subgraph(G, T1):
    Gs = nx.Graph()

    for u, v in T1.edges():
        path = nx.shortest_path(G, u, v, weight='weight')

        for node in path:
            Gs.add_node(node)

        for i in range(len(path) - 1):
            Gs.add_edge(path[i], path[i + 1], weight=G[path[i]][path[i + 1]]['weight'])

    return Gs


def build_steiner_tree(G, Ts):
    TH = Ts.copy()

    while True:
        leaves = [node for node in TH.nodes() if TH.degree(node) == 1 and not G.nodes[node].get('steiner', False)]

        if not leaves:
            break

        for leaf in leaves:
            edges_to_remove = list(TH.edges(leaf))
            TH.remove_edges_from(edges_to_remove)
            TH.remove_node(leaf)

    return TH


def main():
    for num_nodes in range(6, 13):
        steiner_percentage = 0.7
        max_edge_weight = 50

        G = generate_random_graph(num_nodes, steiner_percentage, max_edge_weight)
        nx.draw(G, with_labels=True, font_weight='bold', node_size=500, node_color='lightcoral', font_size=12,
                edge_color='black', width=2)
        plt.show()
        print("Graph G:", G.edges(data=True))

        steiner_tree = find_steiner_tree(G)

        nx.draw(steiner_tree, with_labels=True, font_weight='bold', node_size=500, node_color='lightcoral', font_size=12,
                edge_color='black', width=2)
        plt.show()

        steiner_tree_weight = sum([steiner_tree[u][v]['weight'] for u, v in steiner_tree.edges()])

        print(f"Graph with {num_nodes} nodes:")
        print(f"Steiner Tree Weight: {steiner_tree_weight}")
        print("\n")


if __name__ == "__main__":
    main()
