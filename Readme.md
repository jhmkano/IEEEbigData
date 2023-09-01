# IEEEBigData2023 CC4MCSLAEnriched
Repository presenting our prototype for IEEE Big Data 2023

The notebook describes our approach to state machine abstraction and compliance checking using the alignment technique. The approach involves three components, namely, the annotation, the abstraction, and the checker.

The first component, the annotation component, is responsible for annotating the events contained in an event log based on a knowledge base. This annotation process identifies whether an event is related to a state or a transition in order to abstract a state machine discovered in the next component.

The second component, the abstraction component, is responsible for discovering a state machine in the event log. This component uses the annotated event log to identify the states and transitions in the log and to construct a state machine model on the basis of patterns.

The last component, the checker, compares the discovered state machine with the defined state machine to identify deviations between what happened and what is defined. This component checks for compliance between the defined state machine and the actual behavior captured in the event log.

Overall, the approach presented in this notebook provides a way to automatically abstract state machines from event logs and to check their compliance with a defined state machine.
