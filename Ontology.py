from owlready2 import * 

onto = get_ontology('http://test.org/onto.owl')

with onto: 
    class stateMachine(Thing):
        pass
    class State(stateMachine):
        pass
    class Start(State):
        pass
    class Execute(State):
        pass
    class Complete(State):
        pass
    class Transition(stateMachine):
        pass
    class eventType(Thing):
        pass
    class isRelatedTo(ObjectProperty, FunctionalProperty):
        domain = [eventType]
        range  = [stateMachine]

Service_Create = eventType('Service_Create', isRelatedTo=Start)
Service_Remove = eventType('Service_Remove', isRelatedTo=Start)
Service_Update = eventType('Service_Update', isRelatedTo=Start)

Container_Create = eventType('Container_Create', isRelatedTo=Execute)
Container_Destroy = eventType('Container_Destroy', isRelatedTo=Execute)

Container_Start = eventType('Container_Start', isRelatedTo=Complete)
Container_Stop = eventType('Container_Stop', isRelatedTo=Complete)

Ressource_Usage = eventType('Ressource_Usage', isRelatedTo=Transition)

def search_ancestors(onto, ask):
    result = onto.search(iri = "*{}".format(ask))
    lcStep = str(result[0].isRelatedTo).split('.')[1]
    smElt = str(result[0].isRelatedTo.is_a[0]).split('.')[1]
    if lcStep == 'Transition':
        smElt = 'Transition'
        lcStep = 'N/A'
    return [smElt, lcStep]
