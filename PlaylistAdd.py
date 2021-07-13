from google.auth.transport.requests import Request
import googleapiclient.discovery
import google_auth_oauthlib
import pickle
import json
import os

# setting scopes for the project
scopes = ['https://www.googleapis.com/auth/youtube']

# Instantiating the credentials as none for the following conditional statements
credentials= None

# pulling the credentials from a saved file if they exist - moving to the next if they don't exist
if os.path.exists('token.pickle'):
    print('Loading credentials from file..')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes= scopes)
        credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

# Importing variables containing the channel ids and the upload playlist ids - these only need to be called once so it makes sense to have them exported to save on quota
with open('Add_To_Playlist.json', 'r') as f:
    atp = json.load(f)

# Assigning variable
add_to_playlist = atp['add_to_playlist']

# instantiating the youtube service
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials= credentials)

# creatting the position of the video in the playlist
playlist_position = 0

# creating while loop to add desired videos to the playlist
while True:
    # creating the api request to add videos to the specified playlist
    playlist_add_request = youtube.playlistItems().insert(
        part= 'snippet',
        body= {
            'snippet': {
                'playlistId': 'PL27p_t1EMmhksCZ4qYGyXDXE1M982uN6v',
                'position': playlist_position,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': str(add_to_playlist[0])
                }
            }
        }
    )
    # sending the request to the service
    pladre_response = playlist_add_request.execute()

    # increment the video position in the playlist
    playlist_position += 1
    # remove the added video from the list of videos to add
    add_to_playlist.pop(0)

    if len(add_to_playlist) < 1 or playlist_position > 99:
        break

# Since adding all the videos in the Add_To_Playlist list would eat up too much quota, 
# I limited the script to add until empty or until it has added 100 videos
overwrite_add = {'add_to_playlist': add_to_playlist}

# Saving what is left to add to the playlist (if there any videos remaining)
with open('Add_To_Playlist.json', 'w') as f:
    json.dump(overwrite_add, f, indent= 2)

# confirmation message
print('Complete: added {} videos to playlist'.format(playlist_position))