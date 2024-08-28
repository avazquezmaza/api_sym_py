import json
import requests # type: ignore
import attUtils
import attRestSym

from datetime import datetime, timedelta
from config import REST_URL, REST_PATH_ROM


################################Vars#########################################################    
# Create a dictionary
params = {}
################################GetServiceProvider#########################################################    

def getServiceProvider(mdn):
    customers = []
    token = attUtils.get_token()
    url = f"{REST_URL}{REST_PATH_ROM}"
    contentTypePost= "application/sym-rom-resource-order-execution-post-v1-hal+json"
    contentTypeGet= "application/sym-rom-resource-order-response-v1-hal+json"

    if attUtils.validate_phone_number(mdn):
        print(f"0::::Valid phone number: {mdn}")
        jsonStringRequest = '{ "orderSpecCode": "EPAP.GetServiceProvider", "resourceId": "666c4e07ff07571e528f3427", "resourceName": "EPAP_TLA", "inputParameters": [ { "name": "mdn", "value": "' + mdn + '" } ], "priority": 0, "sync": false, "sourceReference": { "id": 2, "source": "SYM-WEB" } }'
        data = json.loads(jsonStringRequest)

        print(f"1::::Execute Resource Order Test")
        response =  attRestSym.execute(url, token, "POST", contentTypePost, data)

        id =  response.get('id')
        print(f"2::::Get Id: {id}")

        print(f"3::::Get Result")
        response2 =  attRestSym.execute(url + "/" + id, token, "GET", contentTypeGet)

        inputParameters =  response.get('inputParameters')

        for w2 in inputParameters:
            if w2['name'] == 'mdn':
                serviceProvider = w2['value']    
                break

        print(f"4::::serviceProvider: {serviceProvider}")

    else:
        print(f"00::::Invalid phone number: {mdn}")


# Main
mdn = "8911088284"
getServiceProvider(mdn)