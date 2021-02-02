from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import os


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/drive.file' #one or more scopes (strings)
CLIENT_SECRET = 'client_secret_upfile_server.json'
store = file.Storage ('storage3.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets (CLIENT_SECRET, scope=SCOPES)
    flow.redirect_uri = 'https://www.sindicarne.xyz/informarPago'
    creds = tools.run_flow (flow, store, flags) \
        if flags else tools.run (flow, store)
DRIVE = build ('drive', 'v3', http = creds.authorize(Http()))

FILES = (
    ('archivosSubidos/mati.txt', None),    
)

for filename, mimeType in FILES:
    metadata = {'name':filename}
    if mimeType:
        metadata['mimetype'] = mimeType
    res = DRIVE.files().create(body=metadata,media_body = filename, fields='id,webViewLink, mimeType').execute()
    if res:
        print ('Uploaded "%s" (%s)' % (filename, res['mimeType']))
        print ('webviewlink->   ',res.get('webViewLink'))
        # print('Uploaded file to {url}'.format(url='https://drive.google.com/open?id=' + res.get('id')))
        
        
        


# if res:
#     MIMETYPE = 'application/pdf'
#     data = DRIVE.files().export(fileId=res['id'], mimeType=MIMETYPE).execute()
#     if data:
#         fn = '%s.pdf' % os.path.splitext(filename)[0]
#         with open (fn, 'wb') as fh:
#             fh.write(data)
#         print ('Downloadded "%s" (%s)' % (fn,MIMETYPE))
            