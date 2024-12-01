import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# Create a social network graph
def create_social_network(num_nodes, edge_prob):
    G = nx.erdos_renyi_graph(num_nodes, edge_prob)
    celebrity_node_republican = 0
    celebrity_node_democrat = 1
    if G.has_edge(celebrity_node_democrat, celebrity_node_republican):
        G.remove_edge(celebrity_node_democrat, celebrity_node_republican)

    return G


def initialize_states_and_biases(G, celebrity_node_republican, celebrity_node_democrat,
                                 celebrity_party_democrat, celebrity_party_republican,
                                 concealment_prob, predefined_internal_states):
    all_nodes = set(G.nodes)
    non_celeb_nodes = all_nodes - {celebrity_node_republican, celebrity_node_democrat}

    for node in G.nodes:
        G.nodes[node]['internal_state'] = 'undecided'  # True belief
        G.nodes[node]['public_state'] = 'undecided'  # What they say publicly
        G.nodes[node]['bias'] = random.uniform(0.5, 1.5)  # Bias between 0.5 and 1.5
        G.nodes[node]['concealment_prob'] = concealment_prob  # Probability to conceal true belief

    for celebrity_node, celeb_party in [(celebrity_node_democrat, celebrity_party_democrat), (celebrity_node_republican, celebrity_party_republican)]:
        G.nodes[celebrity_node]['bias'] = 10.0  # Celebrity has much higher influence
        G.nodes[celebrity_node]['internal_state'] = celeb_party  # Celebrity's true belief
        G.nodes[celebrity_node]['public_state'] = celeb_party  # Celebrity's public expression
        G.nodes[celebrity_node]['concealment_prob'] = 0.0  # Celebrity always expresses true belief

    num_predefined = predefined_internal_states
    predefined_nodes = random.sample(list(non_celeb_nodes), num_predefined)

    for node in predefined_nodes:
        G.nodes[node]['internal_state'] = random.choice(['democrat', 'republican'])
        concealment = random.random() < G.nodes[node]['concealment_prob']
        if concealment:
            internal = G.nodes[node]['internal_state']
            G.nodes[node]['public_state'] = 'democrat' if internal == 'republican' else 'republican'
        else:
            G.nodes[node]['public_state'] = G.nodes[node]['internal_state']


# Simulate information cascade
def simulate_cascade(G, celebrity_node_republican, celebrity_node_democrat, threshold):
    celebrity_party_democrat = G.nodes[celebrity_node_democrat]['public_state']
    celebrity_party_republican = G.nodes[celebrity_node_republican]['public_state']
    celebrity_neighbors_democrat = set(G.neighbors(celebrity_node_democrat))
    celebrity_neighbors_republican = set(G.neighbors(celebrity_node_republican))

    states_over_time = []

    def capture_state():
        state_snapshot = {
            node: G.nodes[node]['public_state'] for node in G.nodes
        }
        states_over_time.append(state_snapshot)

    capture_state()
    while True:
        new_voters = []

        for node in G.nodes:
            if G.nodes[node]['public_state'] == 'undecided':  # Only consider undecided voters
                neighbors = list(G.neighbors(node))

                democrat_influence = sum(
                    G.nodes[neighbor]['bias'] for neighbor in neighbors
                    if G.nodes[neighbor]['public_state'] == 'democrat')
                republican_influence = sum(
                    G.nodes[neighbor]['bias'] for neighbor in neighbors
                    if G.nodes[neighbor]['public_state'] == 'republican')

                # If the node is a fan of the celebrity, adopt the celebrity's party
                if node in celebrity_neighbors_democrat:
                    new_voters.append((node, celebrity_party_democrat))
                elif node in celebrity_neighbors_republican:
                    new_voters.append((node, celebrity_party_republican))
                else:
                    if democrat_influence >= threshold:
                        new_voters.append((node, 'democrat'))
                    elif republican_influence >= threshold:
                        new_voters.append((node, 'republican'))

        if not new_voters:
            break  # No more undecided voters, stop the cascade
        for node, party in new_voters:
            G.nodes[node]['internal_state'] = party
            concealment = random.random() < G.nodes[node]['concealment_prob']
            if concealment:
                G.nodes[node]['public_state'] = 'democrat' if party == 'republican' else 'republican'
            else:
                G.nodes[node]['public_state'] = party

        capture_state()

    return states_over_time


def visualize_voting_network(G, celebrity_node_republican, celebrity_node_democrat, title, states_over_time):
    """Visualizes the graph with voters' states and biases."""
    state_colors = {
        'undecided': 'gray',
        'democrat': 'blue',
        'republican': 'red'
    }

    pos = nx.spring_layout(G)

    for step, state in enumerate(states_over_time):
        node_colors = [
            state_colors[state[node]] for node in G.nodes
        ]

        node_sizes = [700 if node == celebrity_node_republican or node == celebrity_node_democrat
                      else 300 for node in G.nodes]

        node_shapes = []
        for node in G.nodes:
            if G.nodes[node]['internal_state'] != G.nodes[node]['public_state']:
                node_shapes.append('s')  # Square for nodes concealing true belief
            else:
                node_shapes.append('o')  # Circle for honest nodes

        plt.figure(figsize=(12, 8))
        for node_shape in set(node_shapes):
            node_list = [node for node, shape in zip(G.nodes, node_shapes) if shape == node_shape]
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=node_list,
                node_color=[node_colors[node] for node in node_list],
                node_shape=node_shape,
                node_size=[node_sizes[node] for node in node_list]  # Use node sizes
            )

        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)

        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Honest', markerfacecolor='black', markersize=10),
            Line2D([0], [0], marker='s', color='w', label='Concealing', markerfacecolor='black', markersize=10)
        ]
        plt.legend(handles=legend_elements, loc='upper right')

        plt.title(f"Cascade Progression - Step {step + 1}")
        plt.axis("off")
        plt.show()


def main():
    num_nodes = 50
    edge_prob = 0.2
    threshold = 2.0
    celebrity_node_democrat = 0  # Designate node 0 as the celebrity
    celebrity_party_democrat = 'democrat'  # Celebrity's party
    celebrity_node_republican = 1
    celebrity_party_republican = 'republican'
    concealment_prob = 0.3
    predefined_internal_states = 10

    # Create the social network
    G = create_social_network(num_nodes, edge_prob)

    # Initialize the states
    initialize_states_and_biases(G, celebrity_node_republican, celebrity_node_democrat,
                                 celebrity_party_democrat, celebrity_party_republican,
                                 concealment_prob, predefined_internal_states)

    states_over_time = simulate_cascade(G, celebrity_node_republican, celebrity_node_democrat, threshold)
    visualize_voting_network(G, celebrity_node_republican, celebrity_node_democrat, "teste", states_over_time)


if __name__ == "__main__":
    main()
