import os
import random
import networkx as nx
import matplotlib.pyplot as plt
import shutil

# Setup logging for real-time data
log_file = open("results/real_time_log.txt", "w")

def log_message(message):
    print(message)  # Output to terminal
    log_file.write(message + "\n")  # Write to log file

def generate_grid_graph(grid_size):
    G = nx.grid_2d_graph(grid_size, grid_size)
    pos = {(x, y): (y, -x) for x, y in G.nodes()}
    for edge in G.edges():
        G.edges[edge]['weight'] = 1
    return G, pos

def simulate_failures(G, failure_probability):
    failed_nodes = [node for node in G.nodes if random.random() < failure_probability]
    G.remove_nodes_from(failed_nodes)

    failed_links = [edge for edge in G.edges if random.random() < failure_probability]
    G.remove_edges_from(failed_links)

    return failed_nodes, failed_links

def dynamic_reroute(G, source, target):
    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def visualize_network(G, pos, failed_nodes, failed_links, path, step, scenario):
    plt.figure(figsize=(8, 8))
    nx.draw(G, pos, with_labels=True, node_size=300, node_color='lightblue')
    nx.draw_networkx_nodes(G, pos, nodelist=failed_nodes, node_color='red')
    nx.draw_networkx_edges(G, pos, edgelist=failed_links, edge_color='red', width=2)
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', width=2)
    plt.title(f"Scenario {scenario}, Step {step}")
    plt.savefig(f"results/scenario_{scenario}_step_{step}.png")
    plt.close()

# Parameters
grid_size = 3
failure_probability = 0.1
steps_per_scenario = 5
num_scenarios = 5

# Create results folder
os.makedirs("results", exist_ok=True)

success_rates = []
steps_summary = []

for scenario in range(1, num_scenarios + 1):
    log_message(f"Scenario {scenario}: Starting simulation.")
    G, pos = generate_grid_graph(grid_size)
    source, target = (0, 0), (grid_size - 1, grid_size - 1)
    success_count = 0

    for step in range(1, steps_per_scenario + 1):
        log_message(f"Step {step}: Simulating failures and re-routing.")
        failed_nodes, failed_links = simulate_failures(G, failure_probability)
        log_message(f"Failed nodes: {failed_nodes}")
        log_message(f"Failed links: {failed_links}")
        path = dynamic_reroute(G, source, target)

        if path:
            log_message(f"Path found: {path}")
            success_count += 1
        else:
            log_message(f"No path found.")

        visualize_network(G, pos, failed_nodes, failed_links, path, step, scenario)

    success_rate = success_count / steps_per_scenario * 100
    success_rates.append(success_rate)
    steps_summary.append(steps_per_scenario)
    log_message(f"Scenario {scenario}: Simulation complete with success rate: {success_rate}%")

# Generate success rates chart
plt.bar(range(1, num_scenarios + 1), success_rates, color='green')
plt.title("Success Rates per Scenario")
plt.xlabel("Scenario")
plt.ylabel("Success Rate (%)")
plt.savefig("results/success_rates.png")
plt.close()

# Generate steps chart
plt.plot(range(1, num_scenarios + 1), steps_summary, marker='o', color='blue')
plt.title("Steps Taken per Scenario")
plt.xlabel("Scenario")
plt.ylabel("Steps")
plt.savefig("results/steps_summary.png")
plt.close()

# Save summary table
with open("results/summary_table.txt", "w") as summary_file:
    summary_file.write("Scenario\tSuccess Rate (%)\tSteps Taken\n")
    for i in range(num_scenarios):
        summary_file.write(f"{i + 1}\t\t{success_rates[i]:.2f}\t\t{steps_summary[i]}\n")

# Cleanup intermediate files
for root, dirs, files in os.walk("results"):
    for file in files:
        if not file.endswith((".png", ".txt")):
            os.remove(os.path.join(root, file))
    for dir in dirs:
        shutil.rmtree(os.path.join(root, dir))

# Final log message and proper file closure
log_message("Analysis complete. Results saved in 'results' folder.")
log_file.close()
