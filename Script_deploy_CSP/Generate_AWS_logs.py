import boto3
import random
import time

# Configuration des informations d'identification AWS
aws_access_key_id = ''
aws_secret_access_key = ''
region_name = ''

# Liste pour stocker les IDs des instances créées
created_instances = []

# Création d'une instance EC2
def create_ec2_instance():
    ec2 = boto3.resource('ec2',
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)

    instance = ec2.create_instances(
        ImageId='ami-0715c1897453cabd1',  # ID de l'image EC2
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',  # Type d'instance EC2 (ex: t2.micro)
        KeyName='test_images',  # Nom de la clé SSH
        SecurityGroupIds=['sg-0a1d8156bb0d0c063'],  # ID du groupe de sécurité
        #SubnetId='vpc-0e069fbf2fba95570'  # ID du subnet
    )

    instance_id = instance[0].id
    created_instances.append(instance_id)
    print("Instance EC2 créée avec l'ID :", instance_id)

# Suppression d'une instance EC2
def delete_ec2_instance(instance_id):
    ec2 = boto3.client('ec2',
                       aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key,
                       region_name=region_name)

    ec2.terminate_instances(
        InstanceIds=[instance_id]
    )

    print("Instance EC2 supprimée avec l'ID :", instance_id)

# Suppression de toutes les instances EC2 créées
def delete_all_created_instances():
    if created_instances:
        for instance_id in created_instances:
            delete_ec2_instance(instance_id)
    else:
        print("Aucune instance EC2 à supprimer.")

    created_instances.clear()

# Fonction pour créer et supprimer des instances EC2 de manière aléatoire pendant une durée donnée
def random_instance_actions(duration_minutes):
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    while time.time() < end_time:
        # Génère un nombre aléatoire pour décider de l'action à effectuer (0 pour créer, 1 pour supprimer)
        action = random.randint(0, 1)

        if action == 0:
            create_ec2_instance()
        else:
            # Vérifie d'abord s'il existe des instances EC2 à supprimer
            if created_instances:
                instance_id = random.choice(created_instances)
                delete_ec2_instance(instance_id)

        # Attend un délai aléatoire entre 10 et 20 secondes avant de passer à la prochaine action
        time.sleep(random.randint(5, 10))

    print("Durée de 10 minutes écoulée. Suppression de toutes les instances EC2 créées.")
    delete_all_created_instances()

# Exemple d'utilisation
if __name__ == '__main__':
    random_instance_actions(15)  # Crée et supprime des instances EC2 de manière aléatoire pendant 10 minutes
