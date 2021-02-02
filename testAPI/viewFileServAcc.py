from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

########## ESTE SCRIPT ES PARA VER LOS FILES DE LA GOOGLE SERVICE ACCOUNT (GSA)
### No va a tne ningun funcionamiento pero el codigo me sirve, ya que puedo acceder a las carpetas que se le compartan, 
### especialemente a la 'compartidoService" donde se van a guardar las boletas

SCOPES = 'https://www.googleapis.com/auth/drive.readonly' #one or more scopes (strings)
CLIENT_SECRET = 'serviceAcc.json'
# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py

credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRET, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)
folder_id = '11ca-pPO2fuqzCJvK_MwXhNQ-FhLuJeMa'
# Call the Drive v3 API


resultsFolders = service.files().list(q = "mimeType = 'application/vnd.google-apps.folder'",fields="files(id, name, webViewLink)").execute() 
folders = resultsFolders.get('files',[])

if not folders:
    print('NO se encontro ninguna carpeta.')
else:
    # print('Files in folder: ', items[0])
    for folder in folders:
        
        print ('folders=> ', folder.get('name'))



results = service.files().list(q = "'11ca-pPO2fuqzCJvK_MwXhNQ-FhLuJeMa' in parents",fields="files(id, name, webViewLink)").execute()
items = results.get('files',[])

if not items:
    print('No files found.')
else:
    for item in items:
        
        print ('item=> ', item)
        
