"""
    Abstraction of state-machine
"""
import pm4py
import pandas as pd

from typing import List
from StateMachine import StateMachine

from datetime import timedelta

def pattern_identification(log: pd.DataFrame, pattern: List, attribute: str):
    """ 
        Return index of pattern in log in DataFrame 
        To Do: 
            - Add functionnalities to define patterns across several attributes
            - Enabled possibilities of eventually follows pattern and several states
    """
    # Identify number of item in pattern
    nbPattern = len(pattern)

    # Construction pattern as string
    ## Begin of request
    pattern_s = f"""log.index[(log['{attribute}'] == '{pattern[0]}')"""
    for item in range(1, nbPattern):
        pattern_s += f""" & (log['{attribute}'].shift(-{item}) == '{pattern[item]}')"""
    ## End of request
    pattern_s += f"""]"""

    # Execution of defined pattern
    indice_p_s = eval(pattern_s)
    return indice_p_s

def state_abstraction(log: pd.DataFrame):
    """
        Return states identified
    """
    ## Declare discovered state machine
    SM_Discovered = StateMachine(
        name=''
    )
    pattern=['Start', 'Execute', 'Complete']

    states_index = pattern_identification(log, pattern, 'lcStep')
    states_name = []

    for i, s in enumerate(states_index, 1):
        S_name = 'S'+str(i)
        states_name.append(S_name)
        SM_Discovered.add_state(StateMachine.state(
            name= S_name,
            type='',
            Resourcerequirements={
                log.loc[s]['Metric'] : log.loc[s]['Value']
            }
        ))
    return SM_Discovered, states_index, states_name

def state_type_abstraction(log: pd.DataFrame, State_Machine_Discovered: StateMachine):
    """
        Apply State-Type Abstraction
    """
    state_nb = len(State_Machine_Discovered.states)
    for state in State_Machine_Discovered.states:
        if state.name == 'S1':
            state.set_type('isInitial')
        elif int(state.name[1:]) < state_nb:
            state.set_type('isNormal')
        elif int(state.name[1:]) == state_nb:
            state.set_type('isFinal')
    return State_Machine_Discovered

def transition_abstraction(log: pd.DataFrame, State_Machine_Discovered: StateMachine, states_index):
    """
        Abstraction transition by combining reconfiguration actions and triggering event associated to the state-machine

    """
    states = State_Machine_Discovered.states
    for idx, state in enumerate(states):
        if idx < (len(states) - 1):
            diff_state = int(states[idx+1].Resourcerequirements['replicas']) - int(states[idx].Resourcerequirements['replicas'])

            if diff_state > 0:
                type = 'Scale-out'
            elif diff_state < 0:
                type = 'Scale-in'
            else:
                type = 'Error'
                print('Error: State Equivalent')

            #### Get states Event
            # Set time window selected
            time_window = timedelta(minutes=1)

            # Select events in the time window before state execution
            pattern_ts = log.loc[states_index[idx+1]]['time:timestamp']
            pattern_ts_minus_tw = (pattern_ts - time_window).isoformat()
            transition_Window = log[ ( log['time:timestamp'] > pattern_ts_minus_tw) & \
                (log['time:timestamp'] < pattern_ts) & (log['smElt'] == 'Transition' )].astype({'Value': int})
            
            # Return for each metric observed a consumption average
            avg = transition_Window.groupby('Metric')['Value'].mean().to_dict()

            if bool(avg) != False:
                State_Machine_Discovered.add_transition(
                    StateMachine.transition(
                        name=f"T{idx+1}",
                        source=state.name,
                        target=states[idx+1].name,
                        events=[StateMachine.event(
                                    id = 'E1',
                                    type = 'ResourceRelatedEvent',
                                    predicate = {
                                        'metric': 'Cpu Usage',
                                        'operator': '>=',
                                        'refValue': avg['Cpu Usage'],
                                        'time': str(time_window.total_seconds()) + 's'
                                    })],
                        actions=[StateMachine.action(
                            id = 'A1',
                            type = type,
                            attributes= {
                                'replicas' : abs(diff_state)
                            }
                        )]
                ))

    return State_Machine_Discovered

##### Importation of annotated event logs #####
file_path = 'tmp/exported.xes'
event_log = pm4py.read_xes(file_path)

# Filter by case
events = event_log.groupby('@@case_index')
for i, case_event_log in events:
    ##### State abstraction : Pattern 3.1 #####
    #print("State abstraction : Pattern 3.1")
    SM_Discovered, states_index, states_name = state_abstraction(case_event_log)
    
    ##### State-Type abstraction : Pattern 3.2 #####
    #print("State-Type abstraction : Pattern 3.2")
    SM_Discovered = state_type_abstraction(case_event_log, SM_Discovered)

    ##### Transition abstraction : Pattern 3.3 + 3.4 #####
    #print("Transition abstraction : Pattern 3.4")
    SM_Discovered = transition_abstraction(case_event_log, SM_Discovered, states_index)

    json = SM_Discovered.to_json()

    with open("SM_discovered/SM_.json", "w") as outfile:
        outfile.write(json)

