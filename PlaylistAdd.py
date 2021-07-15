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

# Importing variables containing the channel ids and the upload playlist ids
with open('Add_To_Playlist.json', 'r') as f:
    atp = json.load(f)

# Importing target playlist from Vars.json
with open('Vars.json', 'r') as file:
    vars = json.load(file)

# Assigning variables
add_to_playlist = atp['add_to_playlist']
target_playlist = vars['My_Playlist']

# instantiating the youtube service
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials= credentials)

# creating a variable to track the number of videos added.
video_track = 0

# Creating an empty list to store the popped values from the Add_To_Playlist video
to_archive = []
# creating while loop to add desired videos to the playlist
while True:
    # Popping the last value from the list and saving the output to be used as an archive of what was added to the playlist.
    lifo_videoId = str(add_to_playlist.pop())
    to_archive.append(lifo_videoId)

    # creating the api request to add videos to the specified playlist
    playlist_add_request = youtube.playlistItems().insert(
        part= 'snippet',
        body= {
            'snippet': {
                'playlistId': target_playlist,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': lifo_videoId
                }
            }
        }
    )
    # sending the request to the service
    pladre_response = playlist_add_request.execute()

    # increment the video track
    video_track += 1

    if len(add_to_playlist) < 1 or video_track > 99:
        break

# Since adding all the videos in the Add_To_Playlist list would eat up too much quota, 
# I limited the script to add until empty or until it has added 100 videos
overwrite_add = {'add_to_playlist': add_to_playlist}

# Saving what is left to add to the playlist (if there any videos remaining)
with open('Add_To_Playlist.json', 'w') as f:
    json.dump(overwrite_add, f, indent= 2)

# Loading and extending the list of videos that have been added
with open('Archive_of_added.json', 'r')as file:
    added_videos = json.load(file)

archive_added = added_videos['added_to_playlist']

archive_added.extend(to_archive)

with open('Archive_of_added.json', 'w') as file:
    json.dump(archive_added, file, indent= 2)

# confirmation message
print('Complete: added {} videos to playlist'.format(video_track))
print('Press ENTER To Exit ')