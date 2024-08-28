# utils.py
import requests
import csv
import re
import pytz

from config import USER_FILE, REST_URL, REST_PATH_SSO
from datetime import datetime, timedelta

###########################################################################################
# Create a dictionary
params = {}
# La expresión regular para validar números de 10 y 15 dígitos
patron_10_digitos = re.compile(r'^\d{10}$')
patron_15_digitos = re.compile(r'^\+?\d{15}$')

def validate_phone_number(number):
    # Validar el número
    if patron_10_digitos.match(number) or patron_15_digitos.match(number):
        return True
    
    return False

def read_user_key():
    key_value_pairs = {}
    file = f"{USER_FILE}"
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=':')
        for row in reader:
            key = row[0].strip()
            value = row[1].strip()
            key_value_pairs[key] = value
    return key_value_pairs


def set_global_param(key_value_pairs):
    # Add new parameters to the dictionary
    for k, v in key_value_pairs.items():
        params["username"] = k
        params["password"] = v

def get_token():
    # Función para obtener el token de autenticación
    set_global_param(read_user_key())
    url = f"{REST_URL}{REST_PATH_SSO}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=headers, data=params)
    if response.status_code == 200:
        return response.json()['_embedded']['session']['token']
    else:
        raise Exception("Error al obtener el token")

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