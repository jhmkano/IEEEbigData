import random
import time
import string
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError

# Configuration des informations d'identification Azure
credential = DefaultAzureCredential()
SUBSCRIPTION_ID = ''
RESOURCE_GROUP_NAME = 'Grp_Ressource_1'
location = 'northeurope'

# Liste pour stocker les noms des machines virtuelles créées
created_vms = []

# Création d'une machine virtuelle Azure
def create_vm_in_azure():
    token = ''.join(random.choice(string.digits) for i in range(8))
    VIRTUAL_MACHINE_NAME = f"my-vm-{token}"
    INTERFACE_NAME = f"my-interface-{token}"
    NETWORK_NAME = f"my-network-{token}"

    your_password = 'A1_' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))

    # Create Azure clients
    resource_client = ResourceManagementClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID
    )
    network_client = NetworkManagementClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID
    )
    compute_client = ComputeManagementClient(
        credential=credential,
        subscription_id=SUBSCRIPTION_ID
    )

    # Create resource group
    resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP_NAME,
        {"location": location}
    )

    # Create virtual network
    network_client.virtual_networks.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        NETWORK_NAME,
        {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
    ).result()

    # Create subnet
    subnet = network_client.subnets.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        NETWORK_NAME,
        'subnet1',
        {'address_prefix': '10.0.0.0/24'}
    ).result()

    # Create network interface
    network_interface = network_client.network_interfaces.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        INTERFACE_NAME,
        {
            'location': location,
            'ip_configurations': [{
                'name': 'ipconfig1',
                'subnet': {
                    'id': subnet.id
                }
            }]
        }
    ).result()

    # Create virtual machine
    vm = compute_client.virtual_machines.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        VIRTUAL_MACHINE_NAME,
        {
            "location": location,
            "hardware_profile": {
                "vm_size": "Standard_B1s"
            },
            "storage_profile": {
                "image_reference": {
                    "publisher": "Canonical",
                    "offer": "UbuntuServer",
                    "sku": "18.04-LTS",
                    "version": "latest"
                },
                "os_disk": {
                    "create_option": "fromImage",
                    "managed_disk": {
                        "storage_account_type": "Standard_LRS"
                    }
                }
            },
            "os_profile": {
                "computer_name": VIRTUAL_MACHINE_NAME,
                "admin_username": "azureuser",
                "admin_password": your_password
            },
            "network_profile": {
                "network_interfaces": [
                    {
                        "id": network_interface.id,
                        "properties": {
                            "primary": True
                        }
                    }
                ]
            }
        }
    ).result()

    created_vms.append(vm.name)
    print("Virtual machine created with name:", vm.name)

# Suppression d'une machine virtuelle Azure
def delete_vm_in_azure(vm_name):

    token = vm_name[6:]
    INTERFACE_NAME = f"my-interface-{token}"
    NETWORK_NAME = f"my-network-{token}"

    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    
    try:
        # Récupérer l'interface réseau de la machine virtuelle
        vm = compute_client.virtual_machines.get(RESOURCE_GROUP_NAME, vm_name)
        network_interface_id = vm.network_profile.network_interfaces[0].id

        # Supprimer l'interface réseau
        #network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
        #network_client.network_interfaces.begin_delete(RESOURCE_GROUP_NAME, network_interface_id).result()

        # Supprimer la machine virtuelle
        compute_client.virtual_machines.begin_delete(RESOURCE_GROUP_NAME, vm_name).result()

        # Delete vm_name from list 
        created_vms.remove(vm_name)

        print("Virtual machine deleted with name:", vm_name)

    except ResourceNotFoundError:
        print("Virtual machine not found with name:", vm_name)

    except Exception as e:
        print("An error occurred while deleting the virtual machine:", str(e))

# Suppression de toutes les machines virtuelles Azure créées
def delete_all_created_vms():
    if created_vms:
        for vm_name in created_vms:
            delete_vm_in_azure(vm_name)
    else:
        print("No virtual machines to delete.")

    created_vms.clear()

# Fonction pour créer et supprimer des machines virtuelles Azure de manière aléatoire pendant une durée donnée
def random_vm_actions(duration_minutes):
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)

    print(f"BEGIN: Random VM actions start_time: {start_time} ; end_time: {end_time}")

    while time.time() < end_time:
        # Génère un nombre aléatoire pour décider de l'action à effectuer (0 pour créer, 1 pour supprimer)
        action = random.randint(0, 1)

        if action == 0:
            print("Pick Creating")
            create_vm_in_azure()
        else:
            # Vérifie d'abord s'il existe des machines virtuelles Azure à supprimer
            print(created_vms)
            if created_vms:
                print("Pick Deleting")
                vm_name = random.choice(created_vms)
                delete_vm_in_azure(vm_name)

        # Attend 15 secondes avant de passer à la prochaine action
        print("Wait")
        time.sleep(5)

    print("Duration of {} minutes elapsed. Deleting all created virtual machines.".format(duration_minutes))
    delete_all_created_vms()

# Exemple d'utilisation
if __name__ == '__main__':
    random_vm_actions(30)  # Crée et supprime des machines virtuelles Azure de manière aléatoire pendant
