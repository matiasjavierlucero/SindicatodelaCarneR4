from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
################## Este archivo se usa para que la GOOGLE SERVICE ACC(de ahora en mas GSA) suba archivos a la carpeta de compartida
################## Lo sube a la carpeta 'compartidoService'

SCOPES = 'https://www.googleapis.com/auth/drive.file' #el scope es el 'poder' q le damos al script
CLIENT_SECRET = 'serviceAcc.json' # en este json se guarda la info 'secreta' de la GSA para darle permisos

#aca almacenamos las credenciales
credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRET, scopes=SCOPES)

# creamos un servicio para consumir la api
DRIVE = build('drive', 'v3', credentials=credentials)
folder_id = '11ca-pPO2fuqzCJvK_MwXhNQ-FhLuJeMa' ## este es el ID que le asigno drive a la carpeta 'compartidoService'


# En FILES le pasamos el/los file/s a subir. Tecnicamente no deberia ser mas de 2 x ejecucion,pero x ahora esta en 1
FILES = (
    ('archivosSubidos/alfons.txt', None),    
)
for filename, mimeType in FILES: # aca recorremos FILES y vemos sus atributos
    metadata = {'name':filename, 'parents':[folder_id]} #almacenamos en METADATA el nombre del file y el ID de la carpeta donde se guarda
    if mimeType:
        metadata['mimetype'] = mimeType #si tene mimetype -formato- se lo asigna a metadata
    res = DRIVE.files().create(body=metadata,media_body = filename, fields='id, name, webViewLink, mimeType').execute() #aca ejecutamos todo y obtenemos la info q nos devuelve la query
    if res:
        print ('Uploaded "%s" (%s)' % (filename, res['mimeType']))
        print ('webviewlink->   ',res.get('webViewLink'))



