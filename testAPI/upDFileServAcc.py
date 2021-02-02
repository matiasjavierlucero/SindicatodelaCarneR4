# https://developers.google.com/drive/api/v3/quickstart/python
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
SCOPES = 'https://www.googleapis.com/auth/drive.file' #one or more scopes (strings)
CLIENT_SECRET = 'serviceAcc.json'
# https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py

credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRET, scopes=SCOPES)

# https://developers.google.com/drive/api/v3/quickstart/python
service = build('drive', 'v3', credentials=credentials)

# Call the Drive v3 API


FILES = (
    ('archivosSubidos/MatiasLucero_2021-01-01_3412.pdf', None),    
)
for filename, mimeType in FILES:
    metadata = {'name':filename}
    if mimeType:
        metadata['mimetype'] = mimeType
    res = service.files().create(body=metadata,media_body = filename, fields='id,webViewLink, mimeType').execute()
    if res:
        print ('Uploaded "%s" (%s)' % (filename, res['mimeType']))
        print ('webviewlink->   ',res.get('webViewLink'))


# results = service.files().list(
#     pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get('files', [])

# if not items:
#     print('No files found.')
# else:
#     print('Files:')
#     for item in items:
#         print(u'{0} ({1})'.format(item['name'], item['id']))
