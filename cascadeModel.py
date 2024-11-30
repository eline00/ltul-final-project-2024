import random
import networkx as nx
import matplotlib.pyplot as plt

# Create a social network graph
def create_social_network(num_nodes, edge_prob):
    """Creates a random graph to simulate a social network."""
    G = nx.erdos_renyi_graph(num_nodes, edge_prob)
    return G

# Initialize the state and bias of nodes
def initialize_states_and_biases(G, celebrity_node, celebrity_party):
    """Sets the initial states of the nodes in the graph."""
    for node in G.nodes:
        G.nodes[node]['state'] = 'undecided'  # Voting choice: 'undecided', 'democrat', 'republican'
        G.nodes[node]['bias'] = random.uniform(0.5, 1.5)  # Bias between 0.5 and 1.5
    
    # Set celebrity node with a very high bias
    G.nodes[celebrity_node]['bias'] = 10.0  # Celebrity has much higher influence
    G.nodes[celebrity_node]['state'] = celebrity_party  # Celebrity starts as an adopter

# Simulate information cascade
def simulate_cascade(G, celebrity_node, threshold):
    """Simulates the information cascade process."""
    celebrity_party = G.nodes[celebrity_node]['state']
    celebrity_neighbors = set(G.neighbors(celebrity_node))
    
    while True:
        new_voters = []
        
        for node in G.nodes:
            if G.nodes[node]['state'] == 'undecided':  # Only consider undecided voters
                neighbors = list(G.neighbors(node))
                # If the node is a fan of the celebrity, adopt the celebrity's party
                if node in celebrity_neighbors:
                    new_voters.append((node, celebrity_party))
                else:
                    # Normal threshold-based voting for non-fans
                    democrat_influence = sum(G.nodes[neighbor]['bias'] for neighbor in neighbors if G.nodes[neighbor]['state'] == 'democrat')
                    republican_influence = sum(G.nodes[neighbor]['bias'] for neighbor in neighbors if G.nodes[neighbor]['state'] == 'republican')

                    if democrat_influence >= threshold:
                        new_voters.append((node, 'democrat'))
                    elif republican_influence >= threshold:
                        new_voters.append((node, 'republican'))

        if not new_voters:
            break  # No more undecided voters, stop the cascade
        for node, party in new_voters:
            G.nodes[node]['state'] = party


# Visualize the voting network
def visualize_voting_network(G, celebrity_node):
    """Visualizes the graph with voters' states and biases."""
    state_colors = {
        'undecided': 'gray',
        'democrat': 'blue',
        'republican': 'red'
    }
    node_colors = [
        state_colors[G.nodes[node]['state']] for node in G.nodes
    ]
    node_sizes = [G.nodes[node]['bias'] * 500 for node in G.nodes]  # Size reflects bias
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes)
    labels = {node: f"\n({G.nodes[node]['bias']:.2f})" for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels)
    plt.show()

# Main function to simulate and visualize
def main():
    num_nodes = 50
    edge_prob = 0.2
    threshold = 2.0
    celebrity_node = 0  # Designate node 0 as the celebrity
    celebrity_party = 'democrat'  # Celebrity's party
    
    # Create the social network
    G = create_social_network(num_nodes, edge_prob)

    # Initialize the states
    initialize_states_and_biases(G, celebrity_node, celebrity_party)

    # Visualize initial state
    print("Initial Network State:")
    visualize_voting_network(G, celebrity_node)

    # Simulate the cascade
    adoption_count = simulate_cascade(G, celebrity_node, threshold)
    print(f"Total nodes that adopted the information: {adoption_count}")

    # Visualize final state
    print("Final Network State:")
    visualize_voting_network(G, celebrity_node)

if __name__ == "__main__":
    main()
