import csv
import json
import requests # type: ignore
from datetime import datetime, timedelta
import pytz

from sendEmail import send_email

################################Vars#########################################################    

# Ambiente, cambiar variable
enviroment = "att-mx" # prod
#enviroment = "att-mx-lab" # lab

daysToSeach = 500

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
    before_date = today_date - timedelta(days=daysToSeach)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(like(orderType,DISCONNECT*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*),eq(state,COMPLETED)),sort(-orderDate),limit(0,500)"
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
            with open('out_ml_serviceOrders_Disconnect.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'portIn', 'serviceProvider'])

                for x in content:
                    category = x['category']
                    state = x['state']
                    startDate = x['startDate']
                    completionDate = x['completionDate']
                    orderType = x['orderType']
                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']
                    extraValues = x['extraValues']

                    if len(extraValues) > 1:                       
                        for ev1 in extraValues:
                            if ev1['name'] == 'PORT_IN':
                                portIn = ev1['value']
                                break
                                
                        for ev2 in extraValues:
                            if ev2['name'] == 'SERVICE_PROVIDER':
                                serviceProvider = ev2['value']
                                break
                    else: 
                        portIn = '-'
                        serviceProvider = '-'

                    for y in relatedParty:
                        customer = y['name']

                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, subtract_hours(startDate, 6), subtract_hours(completionDate, 6), orderType, executionTimeMS, customer, portIn, serviceProvider ])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")

def getServiceOrdersMLAll(token):
    print("002 - getServiceOrdersMLAll")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=daysToSeach)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    # params_get = {
    #     "rql": f"and(like(orderType,NEW*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*),or(eq(state,FAILED),eq(state,PARTIAL),eq(state,COMPLETED))),sort(-orderDate),limit(0,500)"
    # }
    params_get = {
        "rql": f"and(like(orderType,*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,MOBILE_LINE*)),sort(-orderDate),limit(0,500)"
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
            with open('out_ml_serviceOrders.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'action', 'imsi', 'mdn','portIn','serviceProvider', 'supension_profile', 'messageError'])

                for x in content:
                    portIn="-"
                    serviceProvider="-"
                    category = x['category']
                    state = x['state']
                   
                    orderType = x['orderType']

                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']
                    orderItems = x['orderItems']
                    extraValues = x['extraValues']

                    if not (x.get('startDate') is None):
                         startDate = x['startDate']
                    else:
                         startDate = '-'


                    if not (x.get('executionTimeInMillis') is None):
                         completionDate = x['completionDate']
                    else:
                         completionDate = '-'

                    for y in relatedParty:
                        customer = y['name']

                    for ev1 in extraValues:
                        if ev1['name'] == 'PORT_IN':
                            portIn = ev1['value']
                            break

                    for ev2 in extraValues:
                        if ev2['name'] == 'SERVICE_PROVIDER':
                            serviceProvider = ev2['value']
                            break

                    if len(orderItems) > 1:
                        z= orderItems[1]
                        action = z['action']
                        service = z['service']

                        if not (service.get('characteristics') is None):
                            characteristics = service['characteristics']
                        
                            for w1 in characteristics:
                                if w1['name'] == 'IMSI':
                                    imsi = w1['value']    
                                    break
                                else:
                                    imsi = '-'

                            for w2 in characteristics:
                                if w2['name'] == 'MDN':
                                    mdn = w2['value']    
                                    break
                                else:
                                    mdn = '-'

                            for w3 in characteristics:
                                if w3['name'] == 'SUSPENSION_PROFILE':
                                    supension_profile = w3['value']    
                                    break
                                else:
                                    supension_profile = '-'

                        errors = z['errors']
                        if len(errors) > 0:
                            for err1 in errors:
                                messageError = err1.get('message')  
                                break
                        else:
                            messageError = "-"
                    else:
                        z= orderItems[0]
                        action = z['action']
                        service = z['service']

                        if not (service.get('characteristics') is None):
                            characteristics = service['characteristics']
                        
                            for w1 in characteristics:
                                if w1['name'] == 'IMSI':
                                    imsi = w1['value']    
                                    break
                                else:
                                    imsi = '-'

                            for w2 in characteristics:
                                if w2['name'] == 'MDN':
                                    mdn = w2['value']    
                                    break
                                else:
                                    mdn = '-'

                            for w3 in characteristics:
                                if w3['name'] == 'SUSPENSION_PROFILE':
                                    supension_profile = w3['value']    
                                    break
                                else:
                                    supension_profile = '-'
                        
                        errors = z['errors']
                        if len(errors) > 0:
                            for err1 in errors:
                                messageError = err1.get('message')  
                                break
                        else:
                            messageError = "-"

                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, subtract_hours(startDate, 6), subtract_hours(completionDate, 6), orderType, executionTimeMS, customer, action, imsi, mdn, portIn, serviceProvider, supension_profile, messageError])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")


def getServiceOrdersOTTDisconnect(token):
    print("004 - getServiceOrdersOTTDisconnect")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=daysToSeach)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(like(orderType,DISCONNECT*),gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,OTT_SERVICE*),eq(state,COMPLETED)),sort(-orderDate),limit(0,500)"
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
            #print("002 - content ", content)
            count = len(content)
            print("Number of JSON objects:", count)

            # Create a CSV file
            with open('out_ott_serviceOrders_Disconnect.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'portIn', 'serviceProvider'])

                for x in content:
                    category = x['category']
                    state = x['state']
                    startDate = x['startDate']
                    completionDate = x['completionDate']
                    orderType = x['orderType']
                    executionTimeMS = x['executionTimeInMillis']
                    relatedParty = x['relatedParty']
                    extraValues = x['extraValues']

                    if len(extraValues) > 1:                       
                        for ev1 in extraValues:
                            if ev1['name'] == 'PORT_IN':
                                portIn = ev1['value']
                                break
                                
                        for ev2 in extraValues:
                            if ev2['name'] == 'SERVICE_PROVIDER':
                                serviceProvider = ev2['value']
                                break
                    else: 
                        portIn = '-'
                        serviceProvider = '-'

                    for y in relatedParty:
                        customer = y['name']

                    # Write each row of data
                    if customer.startswith('CXA') or customer.startswith('CT'):
                        writer.writerow([category, state, subtract_hours(startDate, 6), subtract_hours(completionDate, 6), orderType, executionTimeMS, customer, portIn, serviceProvider ])


    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")



def getServiceOrdersOTTAll(token):
    print("002 - getServiceOrdersAll")

    # Get today's date
    #newMexicoTz = pytz.timezone("America/Mexico_City") 
    today_date = datetime.now() + timedelta(days=1)
    before_date = today_date - timedelta(days=daysToSeach)

    # Format the date as "Month Day, Year"
    formatted_date_today = today_date.strftime("%Y-%m-%dT%H:%M") +  ":00.000Z"
    formatted_date_before = before_date.strftime("%Y-%m-%dT") +  "06:00:00.000Z"

    params_get = {
        "rql": f"and(gt(orderDate,{formatted_date_before}),lt(orderDate,{formatted_date_today}),like(category,OTT_SERVICE*)),sort(-orderDate),limit(0,100)"
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
            with open('out_ott_serviceOrders.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(['category', 'state', 'startDate', 'completionDate', 'orderType', 'time', 'customer', 'action', 'MSISDN', 'SUPPLIER', 'SKU', 'EMAIL'])

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

                    z= orderItems[0]
                    action = z['action']
                    service = z['service']

                    if not (service.get('characteristics') is None):
                        characteristics = service['characteristics']

                        for w1 in characteristics:
                            if w1['name'] == 'MSISDN':
                                msisdn = w1['value']    
                                break

                        for w2 in characteristics:
                            if w2['name'] == 'SUPPLIER':
                                supplier = w2['value']    
                                break
                        
                        for w2 in characteristics:
                            if w2['name'] == 'SKU':
                                sku = w2['value']    
                                break

                        
                        for w2 in characteristics:
                            if w2['name'] == 'EMAIL':
                                email = w2['value']    
                                break

                    else:
                         characteristics = '-'
                         msisdn = ''
                         supplier = ''
                         sku = ''
                         email = ''

                    # Write each row of data
                    if customer.startswith('CTX') or customer.startswith('CX'):
                        writer.writerow([category, state, subtract_hours(startDate, 6), subtract_hours(completionDate, 6), orderType, executionTimeMS, customer, action, msisdn, supplier,sku, email])


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


def subtract_hours(date_string, hours):

    if date_string != '-':
        # Parse the date string into a datetime object
        dt = datetime.fromisoformat(date_string)
        
        # Set the timezone to UTC (you can change this to your desired timezone)
        dt = dt.replace(tzinfo=pytz.UTC)
        
        # Subtract the hours
        dt -= timedelta(hours=hours)
        
        return dt.isoformat()
    else: 
        return "In Progress"

# Main
set_global_param(read_user_key('inFiles/user.key'))
token  = get_token()

getServiceOrdersDisconnect(token)
getServiceOrdersMLAll(token)
getServiceOrdersOTTAll(token)


# getServiceOrdersOTTDisconnect(token)

# execute_OTA_Force_Refresh(token)
