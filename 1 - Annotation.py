"""
    Annotation of event logs 
"""
#### Ontology ####
from owlready2 import * 

##### Create new ontology #####
onto = get_ontology('http://test.org/onto.owl')

##### Ontology Definition #####
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

##### Ancestors Calling #####
def search_ancestors(onto, ask):
    result = onto.search(iri = "*{}".format(ask))
    if result != []:
        lcStep = str(result[0].isRelatedTo).split('.')[1]
        smElt = str(result[0].isRelatedTo.is_a[0]).split('.')[1]
        if lcStep == 'Transition':
            smElt = 'Transition'
            lcStep = 'N/A'
        return [smElt, lcStep]
    else: 
        return ['', '']

#### Pre-processing based on ontology ####
import pandas as pd
import pm4py

#### Import event-logs from 
# 1 : Docker Swarm
# 2 : AWS
# 3 : Azure
# 4 : Gcloud

Dataset = 1

### Docker Swarm
if Dataset == 1 :
    dataframe = pd.read_csv('Datasets/DockerSwarm_logs.csv', sep=',')
    dataframe = pm4py.format_dataframe(dataframe, case_id='Resource Name', activity_key='Event-Type', timestamp_key='Timestamp')
    
### AWS 
elif Dataset == 2 :
    with open('Datasets/AWS_Logs.txt', 'r') as file:
        data = file.read()

    # Split the data into lines
    lines = data.strip().split('\n')

    # Extract the timestamp and JSON object from each line
    records = []
    for line in lines:
        timestamp, json_data = line.split('\t')
        record = {
            'timestamp': timestamp,
            'data': json_data.strip()
        }
        records.append(record)

    # Convert the records to a DataFrame
    df = pd.DataFrame(records)

    # Extract the relevant information from the JSON object
    df['version'] = df['data'].apply(lambda x: eval(x)['version'])
    df['id'] = df['data'].apply(lambda x: eval(x)['id'])
    df['detail-type'] = df['data'].apply(lambda x: eval(x)['detail-type'])
    df['source'] = df['data'].apply(lambda x: eval(x)['source'])
    df['account'] = df['data'].apply(lambda x: eval(x)['account'])
    df['Timestamp'] = df['data'].apply(lambda x: eval(x)['time'])
    df['region'] = df['data'].apply(lambda x: eval(x)['region'])
    df['resources'] = df['data'].apply(lambda x: eval(x)['resources'])
    df['instance-id'] = df['data'].apply(lambda x: eval(x)['detail']['instance-id'] if 'instance-id' in eval(x)['detail'] else None)
    df['state'] = df['data'].apply(lambda x: eval(x)['detail']['state'] if 'state' in eval(x)['detail'] else None)
    df['result'] = df['data'].apply(lambda x: eval(x)['detail']['result'] if 'result' in eval(x)['detail'] else None)
    df['cause'] = df['data'].apply(lambda x: eval(x)['detail']['cause'] if 'cause' in eval(x)['detail'] else None)
    df['Event-Type'] = df['data'].apply(lambda x: eval(x)['detail']['event'] if 'event' in eval(x)['detail'] else None)
    df['request-id'] = df['data'].apply(lambda x: eval(x)['detail']['request-id'] if 'request-id' in eval(x)['detail'] else None)

    # Remove unnecessary columns
    dataframe = df.drop(['data'], axis=1)
    dataframe = pm4py.format_dataframe(dataframe, case_id='resources', activity_key='Event-Type', timestamp_key='Timestamp')

### Azure
elif Dataset == 3 :
    dataframe = pd.read_csv('Datasets/Azure_Logs.csv', sep=',')
    dataframe['Event-Type'] = dataframe["Nom de l'opération"]
    dataframe = pm4py.format_dataframe(dataframe, case_id='Ressource', activity_key="Nom de l'opération", timestamp_key='Heure')

### Gcloud
elif Dataset == 4 : 
    dataframe = pd.read_csv('Datasets/Gcloud_logs.text', sep=',')
    dataframe = pm4py.format_dataframe(dataframe, case_id='Resource Name', activity_key='Event-Type', timestamp_key='Timestamp')

#### Iterate through event logs ####
for idx, row in dataframe.iterrows():
    # Search event type in ontology and returns ancestors 
    smElt, lcStep = search_ancestors(onto, row['Event-Type'])
    dataframe.loc[[idx],'smElt'] = smElt
    dataframe.loc[[idx],'lcStep'] = lcStep

### Export as XES ###
event_log = pm4py.convert_to_event_log(dataframe)
xes = pm4py.write_xes(event_log, 'tmp/exported.xes')