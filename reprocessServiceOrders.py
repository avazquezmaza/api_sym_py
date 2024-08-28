import csv
import re
import logging
import json
import requests # type: ignore
from datetime import datetime
import pandas as pd

################################Vars#########################################################    
# Ambiente, cambiar variable
enviroment = "att-mx" # prod
#enviroment = "att-mx-lab" # lab

customers = []
bulkOrderList = []
# Create a dictionary
params = {}

url = f"https://{enviroment}.symphonica.com:443/sso_rest/authentication/login"
url_get = f"https://{enviroment}.symphonica.com:443/inventory-manager/api/services"
url_ota_refresh = f"https://{enviroment}.symphonica.com:443/workflow-order-manager/api/workflow-orders"


# La expresión regular para validar números de 10 y 15 dígitos
patron_10_digitos = re.compile(r'^\d{10}$')
patron_15_digitos = re.compile(r'^\+?\d{15}$')
################################Class#########################################################    

class Customer:
    def __init__(self, publicIdentifier, party, phoneNumber):
        self.publicIdentifier = publicIdentifier
        self.party = party
        self.phoneNumber = phoneNumber

    def __repr__(self):
        return "Customer publicIdentifier:% s party:% s phoneNumber:% s" % (self.publicIdentifier, self.party, self.phoneNumber)

################################Get Token#########################################################    

def get_token():
    print("Get Token ", url)

    response = requests.post(url, data=params)

    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        # Obtener el contenido de la respuesta en formato JSON
        data = response.json()

        # Obtener valores del diccionario
        return data['_embedded']['session']['token']
    else:
        print("Error al token")

def validate_phone_number(number):
    # Validar el número
    if patron_10_digitos.match(number) or patron_15_digitos.match(number):
        return True
    
    return False

def read_file_line_by_line(file_name, token):
    print("003 - read_file_line_by_line")
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading and trailing whitespaces
            if validate_phone_number(line):
                print(f"Valid phone number: {line}")
                
                params_get = {
                    "rql": f"and(eq(type,CFS),eq(serviceSpecification.name,MOBILE_LINE),eq(serviceCharacteristics.value,{line})),limit(0,10)"
                }

                headers_get = {
                    "x-organization-code": "ATT-MX",
                    "Content-Type": "application/iway-inventory-manager-logical-resource-post-v1-hal+json",
                    "x-authorization": f"{token}"
                }
                
                try:
                    responseGet = requests.get(url_get, headers=headers_get, params=params_get)
                    responseGet.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

                    if responseGet.status_code == 200:
                        data_get = responseGet.json()
                        content = data_get['content']

                        if len(content) > 0:
                            for x in content:
                                publicIdentifier = x['publicIdentifier']
                                relatedParty = x['relatedParty']

                            for y in relatedParty:
                                relatedParty_name = y['name']

                            customers.append(Customer(publicIdentifier, relatedParty_name, line))
                        else:
                            print(f"Phone number: {line} not found")

                    else:
                        print("Error:", responseGet.status_code)
                    
                except requests.exceptions.HTTPError as errh:
                    print(f"Error HTTP: {errh}")
                except requests.exceptions.ConnectionError as errc:
                    print(f"Error de conexión: {errc}")
                except requests.exceptions.Timeout as errt:
                    print(f"Error de tiempo de espera: {errt}")
                except requests.exceptions.RequestException as err:
                    print(f"Error de solicitud: {err}")

            else:
                print(f"Invalid phone number: {line}")

def execute_GLS_Force_Refresh(token):
    print("004 - execute_OTA_Force_Refresh")
    for customer in customers:
        # Getting the current date and time
        dt = datetime.now()

        # getting the timestamp
        ts = datetime.timestamp(dt)
        externalId = f"one_{ts}"

        # Define the JSON payload
        payload = { "externalId": externalId, "category": "MOBILE_LINE", "cfs": { "publicIdentifier": customer.publicIdentifier, "source": "SYM-INVENTORY" }, "relatedParty": [ { "id": customer.party, "source": "BSS", "name": customer.party, "role": "CUSTOMER" } ], "source": "SYM-WOM", "workflowOrderSpec": { "source": "SYM-WOM", "code": "HPESA.GLS.Force.Refresh" }, "desc": "Mobile HPESA GLS Force Refresh" }

        # Set the headers with the token
        headers_ota_refresh = {
            "x-organization-code": "ATT-MX",
            "Content-Type": "application/iway-workflow-order-post-v1-hal+json",
            "x-authorization": f"{token}",
            "X-Language": "en"
        }

        # Convert the payload to JSON
        json_payload = json.dumps(payload)

        # Send the POST request
        try:
            response_ota_refresh = requests.post(url_ota_refresh, headers=headers_ota_refresh, data=json_payload)
            response_ota_refresh.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

            if response_ota_refresh.status_code == 200 | response_ota_refresh.status_code == 201:
                print("Good:", response_ota_refresh)
            else:
                print("Error:", response_ota_refresh.status_code)
                
        except requests.exceptions.HTTPError as errh:
            print(f"Error HTTP: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error de conexión: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Error de tiempo de espera: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"Error de solicitud: {err}")

def read_user_key(file_name):
    print("000 - read_user_key")
    key_value_pairs = {}
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter=':')
        for row in reader:
            key = row[0].strip()
            value = row[1].strip()
            key_value_pairs[key] = value
    return key_value_pairs


def set_global_param(key_value_pairs):
    print("001 - set_global_param")
    # Add new parameters to the dictionary
    for k, v in key_value_pairs.items():
        params["username"] = k
        params["password"] = v

#Guarda archivo en csv
def create_bulkOrders_GLS(data):
    print("0042 - create_bulkOrders_GLS")
    # Getting the current date and time
    dt = datetime.now()
    date_string = dt.strftime('%Y%m%d')

    # # getting the timestamp
    # ts = datetime.timestamp timestamp(dt)
    nameFile = f"bulkOrders_GLS_{date_string}.csv"
    
    # Iterate over the data and write to the output file
    with open(nameFile, 'w') as ff:
        for item in data:
            ff.write(item)
            ff.write('\n')

#Crea json para bukg
def prepare_bulkOrders_GLS():
    print("0041 - prepare_bulkOrders_GLS")    
    for customer in customers:
        # Getting the current date and time
        dt = datetime.now()

        # getting the timestamp
        ts = datetime.timestamp(dt)
        externalId = f"one_{ts}"

        # Define the JSON payload
        payload = { "externalId": externalId, "category": "MOBILE_LINE", "cfs": { "publicIdentifier": customer.publicIdentifier, "source": "SYM-INVENTORY" }, "relatedParty": [ { "id": customer.party, "source": "BSS", "name": customer.party, "role": "CUSTOMER" } ], "source": "SYM-WOM", "workflowOrderSpec": { "source": "SYM-WOM", "code": "HPESA.GLS.Force.Refresh" }, "desc": "Mobile HPESA GLS Force Refresh" }

        # Convert the payload to JSON
        json_payload = json.dumps(payload)
        bulkOrderList.append(json_payload)

    create_bulkOrders_GLS(bulkOrderList)


# Main
set_global_param(read_user_key('user.key'))
token  = get_token()
read_file_line_by_line('numeros_telefonicos.csv',token)
#print("customers:: ",customers)

prepare_bulkOrders_GLS()
# execute_GLS_Force_Refresh(token)