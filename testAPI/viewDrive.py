from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive.readonly' #one or more scopes (strings)
CLIENT_SECRET = 'client_secret.json'

store = file.Storage ('storage.json')
credz = store.get()
if not credz or credz.invalid:
    flow = client.flow_from_clientsecrets (CLIENT_SECRET, SCOPES)
    credz = tools.run_flow (flow, store)

SERVICE = build ('drive', 'v2', http=credz.authorize(Http()))
files = SERVICE.files().list().execute().get('items', [])
for f in files:
    print ('Nombre: ',f['title'],' MimeType: ', f['mimeType'], f['id'])