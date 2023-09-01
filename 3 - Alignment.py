""" 
    Checker 
""" 
import matplotlib.pyplot as plt
import json
import networkx as nx

def to_graph(SM):
    SM_disc = nx.DiGraph()
    for state in SM['_StateMachine__states']:
        SM_disc.add_node(state['_state__name'], replicas = state['_state__Resourcerequirements']['replicas'], type=state['_state__type'])
    for transition in SM['_StateMachine__transitions']:
        SM_disc.add_edge(transition['_transition__source'], transition['_transition__target'], 
                         name=transition['_transition__name'], events=transition['_transition__events'], actions=transition['_transition__actions'])
    return SM_disc

def get_initial_nodes(graph):
    return [n for n,d in graph.in_degree() if d==0]

def get_final_nodes(graph):
    return [n for n,d in graph.out_degree() if d==0]

### Get Discovered state-machine
SM_Disc = to_graph(json.load(open("SM_discovered/SM_UI.json")))

### Get Defined state-machine
SM_Def = to_graph(json.load(open("SM_Defined.json")))

### Search Space construction
SS = nx.DiGraph()
SS.add_node(0, weight=0)

## Add transition 
for i, (eltx, elty) in enumerate(zip(SM_Disc.nodes, SM_Def.nodes)):
    temp_last_nodes = get_final_nodes(SS)
    # e = epsilon to guarantee end
    e = i*0.1
    if SM_Disc.nodes[eltx]['replicas'] == SM_Def.nodes[eltx]['replicas']:
        # State equivalent 
        SS.add_node(str([eltx,elty]), weight=1+e)
        [SS.add_edge(node, str([eltx,elty])) for node in temp_last_nodes]
    else:
        SS.add_node(str([eltx,'>>']), weight=5+e)
        SS.add_node(str(['>>',elty]), weight=5+e)
        [SS.add_edge(node, str([eltx,'>>'])) for node in temp_last_nodes]
        [SS.add_edge(node, str(['>>',elty])) for node in temp_last_nodes]

### Identify starting and ending nodes of the search space
starting_nodes = get_initial_nodes(SS)
ending_nodes = get_final_nodes(SS)

# Compute the worst possible alignment
y_worst_sum = ((len(SM_Def.nodes) * 2 ) * 5)

### Compute the cost of an identified alignment 
results_path = []
for s in starting_nodes:
    for e in ending_nodes:
        y_optimal = 0
        path = nx.astar_path(SS, s, e)
        for elt in path: y_optimal+=SS.nodes[elt]['weight']
        results_path.append((path, y_optimal))
        fitnessValue = 1 - y_optimal / y_worst_sum

print("Report : ")
print(f"Path : {results_path}")
print(f"Y_Optimal : {round(y_optimal, 2)}")
print(f"FitnessValue : {round(fitnessValue, 2)}")

