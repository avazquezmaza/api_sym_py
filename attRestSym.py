import requests
import json

from config import ORGANIZATION_CODE

def execute(url, token, metodo, contentType, data=None):
    # Función para realizar peticiones al servicio REST
    headers = {
        "X-Organization-Code": f"{ORGANIZATION_CODE}",
        "Content-Type": f"{contentType}",
        "X-Authorization": f"{token}",
        "X-Language": "en",
        "Accept": "*/*"
    }

    try:
        if metodo == "GET":
            response = requests.get(url, headers=headers)
        elif metodo == "GETPARAMS":
            response = requests.get(url, headers=headers, params=data)
        elif metodo == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(data))
        else:
            raise Exception("Método no soportado")

        response.raise_for_status()  # Lanza una excepción si el estado es 4xx o 5xx

        if  response.status_code == 201 or response.status_code == 200:
            response = response.json()
        else:
            print("Error:", response.status_code)
                    
    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Error de tiempo de espera: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error de solicitud: {err}")
    
    return response