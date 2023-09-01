import random
import time
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError

# Chemin vers votre fichier de clé JSON
key_path = ''

# Liste pour stocker les IDs des instances créées
created_instances = []

# Création d'une instance VM dans GCP
def create_vm_in_gcp():
    project_id = 'involuted-bird-291212'
    zone = 'us-central1-a'

    credentials = service_account.Credentials.from_service_account_file(key_path)

    compute = discovery.build('compute', 'v1', credentials=credentials)

    instance_name = 'vm-' + str(random.randint(1000, 9999))
    machine_type = 'zones/us-central1-a/machineTypes/n1-standard-1'
    source_image = 'projects/debian-cloud/global/images/family/debian-10'

    config = {
        'name': instance_name,
        'machineType': machine_type,
        'disks': [{
            'boot': True,
            'autoDelete': True,
            'initializeParams': {
                'sourceImage': source_image,
            }
        }],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [{
                'type': 'ONE_TO_ONE_NAT',
                'name': 'External NAT'
            }]
        }],
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/compute',
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write',
                'https://www.googleapis.com/auth/monitoring.write',
                'https://www.googleapis.com/auth/cloud-platform'
            ]
        }]
    }

    compute.instances().insert(project=project_id, zone=zone, body=config).execute()

    created_instances.append(instance_name)
    print("Machine virtuelle créée dans GCP :", instance_name)

# Suppression d'une instance VM dans GCP
def delete_vm_in_gcp(instance_name):
    project_id = 'involuted-bird-291212'
    zone = 'us-central1-a'

    credentials = service_account.Credentials.from_service_account_file(key_path)

    compute = discovery.build('compute', 'v1', credentials=credentials)

    try:
        compute.instances().delete(project=project_id, zone=zone, instance=instance_name).execute()
        print("Machine virtuelle supprimée dans GCP :", instance_name)
        if instance_name in created_instances:
            created_instances.remove(instance_name)
    except HttpError as e:
        error_message = e.content.decode("utf-8")
        if "was not found" in error_message:
            print("La machine virtuelle à supprimer n'existe pas :", instance_name)
        else:
            print("Une erreur s'est produite lors de la suppression de la machine virtuelle :", error_message)

# Suppression de toutes les instances VM créées
def delete_all_created_instances():
    if created_instances:
        for instance_name in created_instances:
            delete_vm_in_gcp(instance_name)
    else:
        print("Aucune instance VM à supprimer.")

    created_instances.clear()

# Fonction pour créer et supprimer des instances VM de manière aléatoire pendant une durée donnée
def random_instance_actions(duration_minutes):
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    while time.time() < end_time:
        # Génère un nombre aléatoire pour décider de l'action à effectuer (0 pour créer, 1 pour supprimer)
        action = random.randint(0, 1)

        if action == 0:
            create_vm_in_gcp()
        else:
            # Vérifie d'abord s'il existe des instances VM à supprimer
            if created_instances:
                instance_name = random.choice(created_instances)
                delete_vm_in_gcp(instance_name)

        # Attend un délai aléatoire entre 10 et 20 secondes avant de passer à la prochaine action
        time.sleep(random.randint(5, 10))

    print("Durée de 10 minutes écoulée. Suppression de toutes les instances VM créées.")
    delete_all_created_instances()

# Exemple d'utilisation
if __name__ == '__main__':
    random_instance_actions(30)  # Crée et supprime des instances VM de manière aléatoire pendant 10 minutes
