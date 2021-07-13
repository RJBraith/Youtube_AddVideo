# You should only need to run this once -- it collects the playlist ids for the listed channels uploads

from googleapiclient.discovery import build
import json

# Importing the API key from a file that will not be pushed to any version control
with open('YT_API_KEY') as yt_api:
    api_key = yt_api.read()

# A dictionary of the youtube channels I want to fetch from
with open('vars.json', 'r') as file:
    vars_load = json.load(file)

chan_dict = vars_load['chan_dict']

# Unpacking the dictionary to place just the values of the dictionary into a list
chan_list = [*chan_dict.values()]

# Instantiating the youtube api service
youtube = build('youtube', 'v3',  developerKey= api_key)

# Forming a batch request for a channels information
# contentDetails is the dictionary containing relatedPlaylists which contains the uploads playlist ID to be used in the playlistItem.list() method
chan_uploads_request = youtube.channels().list(
    part= 'contentDetails, snippet',
    id= chan_list
)

# making the above request to the youtube api
chup_response = chan_uploads_request.execute()

# Create an empty list to populate with the uploads playlist ids of the channels above
upload_playlists = []

# looping over the channel dictionaries returned and selecting the uploads playlist id and appending it to the upload_lists
for channel in chup_response['items']:
    upload_playlists.append(channel['contentDetails']['relatedPlaylists']['uploads'])

with open('Vars.json', 'r') as file:
    vars_save = json.load(file)

vars_save['chan_dict'] = chan_dict
vars_save['chan_list'] = chan_list
vars_save['upload_playlists'] = upload_playlists

with open('Vars.json', 'w') as file:
    json.dump(vars_save, file, indent= 3)