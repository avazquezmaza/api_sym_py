# config.py
import os

# organization-code
ORGANIZATION_CODE = "ATT-MX"
#ORGANIZATION_CODE = "ATT-MX-LAB"

# Ambiente, cambiar variable
ENVIROMENT = "att-mx" # prod
#ENVIROMENT = "att-mx-lab" # lab

# Configuración del servicio REST
REST_URL = f"https://{ENVIROMENT}.symphonica.com"
REST_TOKEN = ''

REST_PATH_SSO = "/sso_rest/authentication/login"
REST_PATH_SERVICE = "/inventory-manager/api/services"
REST_PATH_ROM = "/rom/api/resource-orders"

# Configuración de la aplicación
APP_NAME = "Create Bulk"
APP_VERSION = "1.0"

###############FILES################
USER_FILE = "inFiles/user.key"
INPUT_FILE = "inFiles/inputBulkOrders.csv"

PATH_OUTPUT_FILE = 'outFiles'
OUTPUT_FILE = PATH_OUTPUT_FILE + '/bulkOrders_'
###############################