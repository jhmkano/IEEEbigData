import json
import networkx as nx

from collections import Counter
from copy import deepcopy

class StateMachine(object):
    class state(object):
        def __init__(self, name, type, occurence, Resourcerequirements=None):
            self.__name = name
            self.__type = type
            self.__Resourcerequirements = set() if Resourcerequirements is None else Resourcerequirements
            self.__occurence = occurence

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __set_type(self, type):
            self.__type = type

        def set_type(self, type):
            self.__type = type

        def __set_occurence(self, occurence):
            self.__occurence = occurence

        def set_occurence(self, occurence):
            self.__occurence = occurence

        def __get_occurence(self):
            return self.__occurence

        def __get_type(self):
            return self.__type

        def __get_Resourcerequirements(self):
            return self.__Resourcerequirements

        def __repr__(self):
            return str("("+self.name+", "+ self.type +", "+ repr(self.Resourcerequirements) +")" )

        def __str__(self):
            return self.__repr__()

        def __eq__(self, other):
            # keep the ID for now in states
            return id(self) == id(other)

        def __hash__(self):
            # keep the ID for now in states
            return id(self)

        def __deepcopy__(self, memodict={}):
            if id(self) in memodict:
                return memodict[id(self)]
            new_state = StateMachine.state(self.name, Resourcerequirements=self.Resourcerequirements)
            memodict[id(self)] = new_state
            for transition in self.in_transitions:
                new_transition = deepcopy(transition, memo=memodict)
                new_state.in_transitions.add(new_transition)
            for transition in self.out_transitions:
                new_transition = deepcopy(transition, memo=memodict)
                new_state.out_transitions.add(new_transition)
            return new_state

        name = property(__get_name, __set_name)
        type = property(__get_type, __set_type)
        Resourcerequirements = property(__get_Resourcerequirements)
        occurence = property(__get_occurence, __set_occurence)

    class transition(object):
        def __init__(self, name, source, target, events=None, actions=None):
            self.__name = name
            self.__source = source
            self.__target = target
            self.__actions = set() if actions is None else actions
            self.__events = set() if events is None else events

        def __get_name(self):
            return self.__name

        def __get_source(self):
            return self.__source
        
        def __get_actions(self):
            return self.__actions

        def __get_events(self):
            return self.__events

        def __get_target(self):
            return self.__target

        def __get_properties(self):
            return self.__properties

        def __repr__(self):
            name_rep = repr(self.name)
            source_rep = repr(self.source)
            target_rep = repr(self.target)
            events_rep = repr(self.events)
            actions_rep = repr(self.actions)
            return "("+name_rep+":"+source_rep+"->"+target_rep+","+events_rep+","+actions_rep+")"

        def __str__(self):
            return self.__repr__()

        def __hash__(self):
            return id(self)

        def __eq__(self, other):
            return self.source == other.source and self.target == other.target

        def __deepcopy__(self, memodict={}):
            if id(self) in memodict:
                return memodict[id(self)]
            new_source = memodict[id(self.source)] if id(self.source) in memodict else deepcopy(self.source,
                                                                                                memo=memodict)
            new_target = memodict[id(self.target)] if id(self.target) in memodict else deepcopy(self.target,
                                                                                                memo=memodict)
            memodict[id(self.source)] = new_source
            memodict[id(self.target)] = new_target
            new_transition = StateMachine.transition(new_source, new_target, weight=self.weight, properties=self.properties)
            memodict[id(self)] = new_transition
            return new_transition

        name = property(__get_name)
        source = property(__get_source)
        target = property(__get_target)
        events = property(__get_events)
        actions = property(__get_actions)
        properties = property(__get_properties)

    class event(object):
        def __init__(self, id, type, predicate):
            self.__id = id
            self.__type = type
            self.__predicate = predicate
        
        def __get_id(self):
            return self.__id
        
        def __get_type(self):
            return self.__type
        
        def __get_predicate(self):
            return self.__predicate
        
        def __repr__(self):
            return f"({self.id},{self.type},{self.predicate})"

        def __str__(self):
            return self.__repr__()
        
        id = property(__get_id)
        type = property(__get_type)
        predicate = property(__get_predicate)

    class action(object):
        def __init__(self, id, type, attributes):
            self.__id = id
            self.__type = type
            self.__attributes = attributes

        def __get_id(self):
            return self.__id

        def __get_type(self):
            return self.__type

        def __get_attributes(self):
            return self.__attributes

        def __repr__(self):
            return f"({self.id},{self.type},{self.attributes})"

        def __str__(self):
            return self.__repr__()

        id = property(__get_id)
        type = property(__get_type)
        attributes = property(__get_attributes)

    def add_state(self, new_state):
        self.states.append(new_state)
        self.__graph.add_node(new_state.name)

    def add_transition(self, new_transition):
        self.transitions.append(new_transition)
        self.__graph.add_edge(new_transition.source, new_transition.target)

    def __init__(self, name=None, states=None, transitions=None):
        self.__name = "" if name is None else name
        self.__states = [] if states is None else states
        self.__transitions = [] if transitions is None else transitions
        self.__graph = nx.DiGraph()

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_states(self):
        return self.__states

    def __get_transitions(self):
        return self.__transitions
    
    def __get_graph(self):
        return self.__graph

    def __hash__(self):
        ret = 0
        for p in self.states:
            ret += hash(p)
            ret = ret % 479001599
        for t in self.transitions:
            ret += hash(t)
            ret = ret % 479001599
        return ret

    def __eq__(self, other):
        # for the Petri net equality keep the ID for now
        return id(self) == id(other)

    def __deepcopy__(self, memodict={}):
        from pm4py.objects.petri_net.utils.petri_utils import add_transition_from_to
        this_copy = StateMachine(self.name)
        memodict[id(self)] = this_copy

        for state in self.states:
            state_copy = StateMachine.state(state.name, properties=state.properties)
            this_copy.states.add(state_copy)
            memodict[id(state)] = state_copy

        for trans in self.transitions:
            trans_copy = StateMachine.Transition(trans.name, trans.label, properties=trans.properties)
            this_copy.transitions.add(trans_copy)
            memodict[id(trans)] = trans_copy

        for transition in self.transitions:
            add_transition_from_to(memodict[id(transition.source)], memodict[id(transition.target)], this_copy, weight=transition.weight)

        return this_copy

    def __repr__(self):
        return f"[Name:{self.name}; States:{self.states}; Transitions:{self.transitions}]"
        #ret = ["States: ["]
        #states_rep = []
        #for state in self.states:
        #    states_rep.append(repr(state))
        #states_rep.sort()
        #ret.append(" " + ", ".join(states_rep) + " ")
        #ret.append("]\nTransitions: [")
        #trans_rep = []
        #for trans in self.transitions:
        #    trans_rep.append(repr(trans))
        #trans_rep.sort()
        #ret.append(" " + ", ".join(trans_rep) + " ")
        #ret.append("]")
        #return "".join(ret)

    def __str__(self):
        return self.__repr__()

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    name = property(__get_name, __set_name)
    states = property(__get_states)
    transitions = property(__get_transitions)
    graph = property(__get_graph)
