from googleapiclient.discovery import build
from datetime import datetime, timedelta
import numpy as np
import json
import re

# Importing the API key from a file that will not be pushed to any version control
with open('YT_API_KEY') as yt_api:
    api_key = yt_api.read()

# Importing variables containing the channel ids and the upload playlist ids - these only need to be called once so it makes sense to have them exported to save on quota
with open('Vars.json', 'r') as f:
    vars_load = json.load(f)

chan_dict = vars_load['chan_dict']
chan_list = vars_load['chan_list']
upload_playlists = vars_load['upload_playlists']

# Loading list of videos that have been added - this avoids adding the same video multiple times over multiple uses
with open('Archive_of_added.json', 'r')as file:
    archive = json.load(file)

archive_added = archive['added_to_playlist']

# Getting current date to compare to videos pulled - I only want videos that are at least a week old so that people have had a chance to see them and like if they desire
current_date = datetime.today()

# setting a format to convert the string format returned by the publishedAt value to a datetime
dt_format = r'%Y-%m-%dT%H:%M:%SZ'

# compiling patterns to deconstruct video duration into number of hours and number of minutes. This is so I can limit additions to videos less than 20 mins
hour_pattern = re.compile(r'(\d+)H')
minute_pattern = re.compile(r'(\d+)M')

# Creating the add to playlist list outside of the while loop so the list is not reset each time the api calls a new page
# Creating list to hold videos to be added to the playlist
# Creating the empty lists for the videos view and like count to be standardized for more consistent processing

marked_for_add = []

chan_video_id = []
chan_like_list = []
chan_view_list = []

video_data = {
    'channel_names': list(chan_dict.keys()),
    'video_Id': [],
    'likeCount': [],
    'viewCount': [],
    'threshold': [],
    'score': [],
}

# Creating a variable to select a channel's uploads playlist
uploadsIndex = 0

# Marking next page token to keep track of which playlist items have and have not being processed
nextPageToken = None

# creating confirmation that the process of finding videos has started:
print('Selecting Videos...')

# Instantiating the youtube api service
youtube = build('youtube', 'v3',  developerKey= api_key)

# Loop over the requests so that I might process playlists with more than 50 videos (50 is the maximum page size you can specify)
while True:
    # Creating the request for the items in the channel's upload playlists
    uploads_request = youtube.playlistItems().list(
        part= 'contentDetails',
        playlistId= upload_playlists[uploadsIndex],
        maxResults= 50,
        pageToken= nextPageToken
    )

    # making the above request to the youtube api
    upre_response = uploads_request.execute()

    # Creating an empty list to populate with video ids from the request above. This will reset to a blank list at the start of a new page request
    vid_ids= []

    # Looping over the upload playlist appending the video ids to the vid_ids list
    for item in upre_response['items']:
        vid_ids.append(item['contentDetails']['videoId'])

    # Creating the request for the videos in the upload playlist
    vid_request = youtube.videos().list(
        part= 'contentDetails, snippet, statistics',
        id= ','.join(vid_ids),
        maxResults= 50
    )

    # making the above request to the youtube api
    vire_response = vid_request.execute()

    # setting condition for video to be marked for the playlist
    for video in vire_response['items']:
        # If the video is not in the archive of videos already added
        if video['id'] not in archive_added:
            # If the video is at least a week old
            if (current_date - datetime.strptime(video['snippet']['publishedAt'], dt_format)) >= timedelta(days= 7):
                duration = video['contentDetails']['duration']

                minutes = (minute_pattern.search(duration))
                minutes = int(minutes.group(1)) if minutes else 0

                hours = (hour_pattern.search(duration))
                hours = int(hours.group(1)) if hours else 0
                # If the video is under 20 minutes long but at least 1 minute long
                if (minutes < 20) and (minutes > 0) and (hours == 0):
                    try:
                        video_id = video['id']
                        chan_video_id.append(video_id)
                        likeCount = int(video['statistics']['likeCount'])
                        chan_like_list.append(likeCount)
                        viewCount = int(video['statistics']['viewCount'])
                        chan_view_list.append(viewCount)
                    except KeyError as l:
                        continue
    # Updating value of page token to get more videos
    nextPageToken = upre_response.get('nextPageToken')
    
    # Setting the conditions for the playlist to swap and the loop to break
    # if the nextPageToken returns none and the uploadsIndex is less than the length of the channel list
    if (not nextPageToken) and (uploadsIndex < len(chan_list)):
        print('Completed processing {}\'s uploads'.format(video_data['channel_names'][uploadsIndex]))
        
        video_data['video_Id'].append(chan_video_id)
        video_data['likeCount'].append(chan_like_list)
        video_data['viewCount'].append(chan_view_list)

        chan_video_id = []
        chan_like_list = []
        chan_view_list = []

        uploadsIndex += 1
    # if the nextPageToken returns none and the uploadsIndex is greater or equal to the length of the channel list, all videos are processed.
    if (not nextPageToken) and (uploadsIndex == len(chan_list)):
        print('Finished...')
        break

# Defining a function that can be used to standardize the likeCount list and viewCount list
class videoCriteria:
    def __init__(self, likeCount, viewCount):
        '''
        Giving the likeCount and viewCount lists, calculates the mean, standard deviation in order to standardize each list

        Calculates a score by:
            Summing the two standardized lists     
        Then calculates a threshold variable which is:
            The sum of the means of each standardized list     
        '''

        self.likeCount = likeCount
        self.lc_mean = np.mean(self.likeCount)
        self.lc_sdev = np.std(self.likeCount)
        self.lc_std = abs((self.likeCount - self.lc_mean) / self.lc_sdev)

        self.viewCount = viewCount
        self.vc_mean = np.mean(self.viewCount)
        self.vc_sdev = np.std(self.viewCount)
        self.vc_std = abs((self.viewCount - self.vc_mean) / self.vc_sdev)

        self.threshold = abs(np.mean(self.lc_std) + np.mean(self.vc_std))
        self.score = (self.lc_std + self.vc_std)

    def threshold(self):
        return self.threshold

    def score(self):
        return self.score

for channel in range(len(video_data['channel_names'])):
    likeCount_list = video_data['likeCount'][channel]
    viewCount_list = video_data['viewCount'][channel]

    video_criteria = videoCriteria(likeCount_list, viewCount_list)

    for video in range(len(likeCount_list)):
        if video_criteria.score[video] > video_criteria.threshold * 1.8:
                # Add the video to the list if the video has views and likes and the standardized ratio of likes to views surpasses the threshold
                marked_for_add.append(video_data['video_Id'][channel][video])

# Adding videos to two jsons, those to be added to the playlist (and popped out) and those to be saved in the list so that videos on that list 
# can't be added to the playlist more than one time
# Loading them in seperate calls so that the edits will extend the length of the list.
with open('Add_To_Playlist.json', 'r') as file:
    atp = json.load(file)

atp['add_to_playlist'].extend(marked_for_add)

with open('Add_To_Playlist.json', 'w') as file:
    json.dump(atp, file, indent= 2)

archive_added.extend(marked_for_add)

with open('Archive_of_added.json', 'w') as file:
    json.dump(archive, file, indent= 2)

print('Operation Complete.. Found {} videos'.format(len(marked_for_add)))