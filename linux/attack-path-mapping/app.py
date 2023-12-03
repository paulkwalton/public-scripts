import networkx as nx
import matplotlib.pyplot as plt

# Function to add nodes and edges to the graph
def add_nodes_and_edges(G, source, targets, firewall_present):
    G.add_node(source['hostname'], environment='Enterprise', ip=source['ip'])
    
    for target in targets:
        G.add_node(target['hostname'], environment='Restricted Network', ip=target['ip'])

        if firewall_present:
            G.add_node('Firewall', environment='Security Layer')
            G.add_edge(source['hostname'], 'Firewall', port='Firewall Port')
            G.add_edge('Firewall', target['hostname'], port='443', method='Exploit B')
        else:
            G.add_edge(source['hostname'], target['hostname'], port='443', method='Exploit B')

# Function to draw the graph
def draw_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)

    # Color nodes based on environment
    node_color = [get_node_color(G.nodes[node]['environment']) for node in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_color)

    nx.draw_networkx_edges(G, pos)
    node_labels = {node: f"{node}\n({G.nodes[node]['ip']})" for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels)

    edge_labels = nx.get_edge_attributes(G, 'port')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Attack Path Mapping Diagram")
    plt.axis('off')
    plt.show()

# Helper function to determine node color based on environment
def get_node_color(environment):
    colors = {
        'Enterprise': 'skyblue',
        'Restricted Network': 'salmon',
        'Security Layer': 'gold'
    }
    return colors.get(environment, 'grey')

# Main program
def main():
    G = nx.DiGraph()

    # User inputs for source
    source_ip = input("Enter the source IP: ")
    source_hostname = input("Enter the source Hostname: ")
    source = {'ip': source_ip, 'hostname': source_hostname}

    # User inputs for targets
    targets = []
    while True:
        target_ip = input("Enter a target IP (or leave blank to finish): ")
        if not target_ip:
            break
        target_hostname = input(f"Enter the hostname for {target_ip}: ")
        targets.append({'ip': target_ip, 'hostname': target_hostname})

    # User input for firewall presence
    firewall_present = input("Is there a firewall in front of the targets? (yes/no): ").lower() == 'yes'

    # Add nodes and edges to the graph
    add_nodes_and_edges(G, source, targets, firewall_present)

    # Draw the graph
    draw_graph(G)

if __name__ == "__main__":
    main()
