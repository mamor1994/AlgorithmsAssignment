import networkx as nx
import random
import matplotlib.pyplot as plt


def create_graph(V, S_percentage, max_weight):
    G = nx.Graph()
    G.add_nodes_from(range(1, V + 1))

    # α) Δημιουργία Steiner κόμβων
    num_steiner_nodes = int(S_percentage * V)
    steiner_nodes = random.sample(list(G.nodes()), num_steiner_nodes)
    print("Steiner nodes selected:", steiner_nodes)
    # Επισύναψη των Steiner κόμβων στο γράφημα
    for node in G.nodes():
        if node in steiner_nodes:
            G.nodes[node]['steiner'] = True
        else:
            G.nodes[node]['steiner'] = False

    # Δημιουργία τυχαίου αριθμού ζευγών κόμβων για σύνδεση
    num_edges = random.randint(V - 1, V * (V - 1) // 2)  # Ελάχιστος και Μέγιστος αριθμός ακμών σε ενα γράφημα

    # Δημιουργία ακμών σε κάθε κορυφή που δεν έχει ακόμα
    for u in G.nodes():
        while G.degree(u) < 1:
            v = random.choice(list(G.nodes()))
            if v != u and G.degree(v) < 2:
                weight = random.randint(1, max_weight)
                G.add_edge(u, v, weight=weight)

    # Ενώσεις κόμβων μέχρι να φτάσουμε τον αριθμό ακμών
    while G.number_of_edges() < num_edges:
        u = random.choice(list(G.nodes()))
        v = random.choice(list(G.nodes()))
        if u != v and not G.has_edge(u, v):
            weight = random.randint(1, max_weight)
            G.add_edge(u, v, weight=weight)

    return G


def steiner_tree_algorithm(G):
    # α) Δημιουργία πλήρους γραφήματος G1
    G1 = complete_graph_from_original(G)
    print("Complete Graph from original G (G1):", G1.edges(data=True))
    # β) Εύρεση ελάχιστου γεννητικού δέντρου T1 του G1
    T1 = nx.minimum_spanning_tree(G1)
    print("Minimum Spanning Tree (T1):", T1.edges(data=True))
    # γ) Κατασκευή υπογράφηματος Gs για Τ1
    Gs = construct_subgraph(G, T1)
    print("Constructed Subgraph (Gs):", Gs.edges(data=True))
    # δ) Εύρεση ελάχιστου γεννητικου δέντρου Ts
    Ts = nx.minimum_spanning_tree(Gs)
    print("Minimum Spanning Tree (Ts):", Ts.edges(data=True))
    # ε) Κατασκευή δέντρου Steiner TH
    TH = construct_steiner_tree(G, Ts)
    print("Steiner Tree (TH):", TH.edges(data=True))
    return TH


def complete_graph_from_original(G):
    G1 = nx.Graph()

    # Προσθήκη μόνο των κόμβων που είναι Steiner κόμβοι στον G1
    steiner_nodes = [node for node in G.nodes() if G.nodes[node].get('steiner', False)]
    G1.add_nodes_from(steiner_nodes)

    # Υπολογισμός των βαρών των ακμών στον G1
    for u, v in G.edges():
        if u != v and u in steiner_nodes and v in steiner_nodes:
            weight = nx.shortest_path_length(G, u, v, weight='weight')
            G1.add_edge(u, v, weight=weight)

    return G1


def construct_subgraph(G, T1):
    for u, v in T1.edges():
        # Βρίσκουμε όλα τα ελάχιστα μονοπάτια
        paths = nx.all_shortest_paths(G, u, v, weight='weight')
        for path in paths:
            Gs = T1.copy()  # Δημιουργία ενός νέου υπογράφου για κάθε ζευγάρι κορυφών
            removed_edges = set()  # Αρχικοποίηση του συνόλου removed_edges ως ένα κενό σύνολο
            if (u, v) not in removed_edges and (v, u) not in removed_edges:  # Ελέγχουμε αν η ακμή έχει ήδη αφαιρεθεί
                if Gs.has_edge(u, v):
                    # Αφαίρεση της υπάρχουσας ακμής
                    Gs.remove_edge(u, v)
                    removed_edges.add((u, v))  # Προσθήκη της ακμής στο σύνολο των αφαιρεθέντων

                    # Προσθήκη των μονοπατιών ως νέες ακμές
                    if not Gs.has_edge(path[0], path[-1]):
                        for i in range(len(path) - 1):
                            Gs.add_edge(path[i], path[i + 1], weight=G[path[i]][path[i + 1]]['weight'])

    return Gs


def construct_steiner_tree(G, Ts):
    TH = Ts.copy()

    while True:
        # Βρίσκουμε τα φύλλα του TH που δεν είναι κορυφές Steiner
        leaves = [node for node in TH.nodes() if TH.degree(node) == 1 and not G.nodes[node].get('steiner', False)]

        # Αν δεν υπάρχουν φύλλα που δεν είναι κορυφές Steiner, τερματίζουμε τη διαδικασία
        if not leaves:
            break

        for leaf in leaves:
            # Διαγράφουμε τις ακμές που είναι συνδεδεμένες με το φύλλο
            edges_to_remove = list(TH.edges(leaf))
            TH.remove_edges_from(edges_to_remove)
            # Διαγράφουμε το φύλλο από το TH
            TH.remove_node(leaf)

    return TH


def main():
    # Υλοποίηση του προγράμματος
    for V in range(6, 13):
        S_percentage = 0.7
        max_weight = 50

        G = create_graph(V, S_percentage, max_weight)
        # Σχεδίαση του γράφου
        nx.draw(G, with_labels=True, font_weight='bold', node_size=500, node_color='skyblue', font_size=12,
                edge_color='black', width=2)
        plt.show()
        print("Graph G:", G.edges(data=True))
        # Εκτέλεση του αλγορίθμου

        steiner_tree = steiner_tree_algorithm(G)

        # Εκτύπωση του γραφήματος
        nx.draw(steiner_tree, with_labels=True, font_weight='bold', node_size=500, node_color='skyblue', font_size=12,
                edge_color='black', width=2)
        plt.show()
        # Εκτύπωση αποτελεσμάτων
        steiner_tree_weight = sum([steiner_tree[u][v]['weight'] for u, v in steiner_tree.edges()])

        print(f"Graph with {V} nodes:")
        print(f"Steiner Tree Weight: {steiner_tree_weight}")


if __name__ == "__main__":
    main()