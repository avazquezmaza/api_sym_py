import csv
import json
import requests # type: ignore
from datetime import datetime, timedelta
import pytz

################################Vars#########################################################    

# Ambiente, cambiar variable
enviroment = "att-mx" # prod
#enviroment = "att-mx-lab" # lab

customers = []
# Create a dictionary
params = {}

url = f"https://{enviroment}.symphonica.com:443/sso_rest/authentication/login"
url_get = f"https://{enviroment}.symphonica.com:443/service-order-manager/api/service-orders"
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

def getServiceOrdersDisconnect(token):
    print("002 - getServiceOrdersDisconnect")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=90)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(like(orderType,DISCONNECT*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*),eq(state,COMPLETED)),sort(-orderDate),limit(0,300)"
    }

    headers_get = {
        "X-Organization-Code": "ATT-MX",
        "Content-Type": "application/iway-service-order-response-v1-hal+json",
        "X-Language": "en",
        "X-Authorization": f"{token}"
    }
    
    try:
        responseGet = requests.get(url_get, headers=headers_get, params=params_get)
        responseGet.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

        # Check if the request was successful
        if responseGet.status_code == 200:
            # Load the JSON response
            data_get = json.loads(responseGet.text)
            content = data_get['content']
            # print("002 - content ", content)
            count = len(content)
            print("Number of JSON objects:", count)

            # Create a CSV file
            with open('serviceOrdersDisconnect.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer'])

                for x in content:
                    category = x['category']
                    state = x['state']
                    startDate = x['startDate']
                    completionDate = x['completionDate']
                    orderType = x['orderType']
                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']

                    for y in relatedParty:
                        customer = y['name']
                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, startDate, completionDate, orderType, executionTimeMS, customer])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")

def getServiceOrdersNew(token):
    print("002 - getServiceOrdersNew")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=90)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(like(orderType,NEW*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*),eq(state,COMPLETED)),sort(-orderDate),limit(0,300)"
    }

    headers_get = {
        "X-Organization-Code": "ATT-MX",
        "Content-Type": "application/iway-service-order-response-v1-hal+json",
        "X-Language": "en",
        "X-Authorization": f"{token}"
    }
    
    try:
        responseGet = requests.get(url_get, headers=headers_get, params=params_get)
        responseGet.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

        # Check if the request was successful
        if responseGet.status_code == 200:
            # Load the JSON response
            data_get = json.loads(responseGet.text)
            content = data_get['content']
            # print("002 - content ", content)
            count = len(content)
            print("Number of JSON objects:", count)

            # Create a CSV file
            with open('serviceOrdersNew.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'action', 'imsi', 'mdn'])

                for x in content:
                    category = x['category']
                    state = x['state']
                    startDate = x['startDate']
                    completionDate = x['completionDate']
                    orderType = x['orderType']
                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']
                    orderItems = x['orderItems']

                    for y in relatedParty:
                        customer = y['name']

                    z= orderItems[1]
                    action = z['action']
                    characteristics = z['service']['characteristics']
                    
                    for w1 in characteristics:
                        if w1['name'] == 'IMSI':
                            imsi = w1['value']    
                            break

                    for w2 in characteristics:
                        if w2['name'] == 'MDN':
                            mdn = w2['value']    
                            break

                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, startDate, completionDate, orderType, executionTimeMS, customer, action, imsi, mdn])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")


def getServiceOrdersError(token):
    print("002 - getServiceOrdersNew")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=90)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(like(orderType,NEW*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*),or(eq(state,FAILED),eq(state,PARTIAL),eq(state,COMPLETED))),sort(-orderDate),limit(0,500)"
    }

    headers_get = {
        "X-Organization-Code": "ATT-MX",
        "Content-Type": "application/iway-service-order-response-v1-hal+json",
        "X-Language": "en",
        "X-Authorization": f"{token}"
    }
    
    try:
        responseGet = requests.get(url_get, headers=headers_get, params=params_get)
        responseGet.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

        # Check if the request was successful
        if responseGet.status_code == 200:
            # Load the JSON response
            data_get = json.loads(responseGet.text)
            content = data_get['content']
            # print("002 - content ", content)
            count = len(content)
            print("Number of JSON objects:", count)

            # Create a CSV file
            with open('serviceOrders2.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'action', 'imsi', 'mdn'])

                for x in content:
                    category = x['category']
                    state = x['state']
                    startDate = x['startDate']
                    completionDate = x['completionDate']
                    orderType = x['orderType']
                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']
                    orderItems = x['orderItems']

                    for y in relatedParty:
                        customer = y['name']

                    z= orderItems[1]
                    action = z['action']
                    characteristics = z['service']['characteristics']
                    
                    for w1 in characteristics:
                        if w1['name'] == 'IMSI':
                            imsi = w1['value']    
                            break

                    for w2 in characteristics:
                        if w2['name'] == 'MDN':
                            mdn = w2['value']    
                            break

                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, startDate, completionDate, orderType, executionTimeMS, customer, action, imsi, mdn])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")

# Lee archivo con user:pass
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


#Definine variables globales de user:pass en headers
def set_global_param(key_value_pairs):
    print("001 - set_global_param")
    # Add new parameters to the dictionary
    for k, v in key_value_pairs.items():
        params["username"] = k
        params["password"] = v

# Main
set_global_param(read_user_key('user.key'))
token  = get_token()
getServiceOrdersDisconnect(token)
#getServiceOrdersNew(token)
getServiceOrdersError(token)

# execute_OTA_Force_Refresh(token)