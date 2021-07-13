 ### Youtube playlist video adder
 I wanted a way of sifting through the music channels that I subscribe to and selecting songs that have above average amounts of likes and views for the channel.
 This was the solution I came up with, given the api constraints -- the daily quota of 10k, adding 200 videos to your playlist a day is the upper limit.
 If you also populate the list of videos to add to the playlist, that 200 decreases.
 
 This was my first attempt at anything like this. I do not think this is 100% efficient and it could be / has been done better. However, inefficiency notwithstanding, I achieved what I set out to produce. 

**Python Version:** 3.9  

**Libraries Used:** numpy, json, re, datetime, os, googleapiclient, google auth

**Resources:** [Youtube API Documentation](https://developers.google.com/youtube) , [Google API Python Doc](https://github.com/googleapis/google-api-python-client/blob/master/docs/README.md) , [Google Library Install](https://developers.google.com/webmaster-tools/search-console-api-original/v3/libraries#python) , [OAuth Credential Snippets](https://gist.github.com/CoreyMSchafer/ea5e3129b81f47c7c38eb9c2e6ddcad7)

#### While I don't expect anyone to go through the trouble to understand the following, the instructions for use are below, moreso for myself and posterity than for public use
#### Steps:

1. [Create google developer account](https://console.developers.google.com/)
2. Create a project
3. Enable the Youtube V3 API inside the [api dashboard](https://console.cloud.google.com/apis/dashboard)
4. Create some credentials by navigating to APIs & Services and selecting Credentials then create an API key and OAuth client ID (Choose Desktop App)
   
   ![](https://user-images.githubusercontent.com/68555817/125516496-3d53f90a-11c0-4efa-bb15-b18af14a117b.png)
5. Paste your API key into the YT_API_KEY file and save it.
6. Download your client_secrets file, place it in the same directory as the python scripts and rename it to client_secret making sure it has the json extension
   ![](https://user-images.githubusercontent.com/68555817/125517152-d7f64c8d-c680-4b0c-b7ac-93751f133023.png)
   ![](https://user-images.githubusercontent.com/68555817/125517213-f9ce7e22-1e1a-4a9c-b0c5-3f776a55f6e8.png)
7. Collect the channel ids of the channels whose videos you want to be searched. Visit their channel and copy the highlighted area:
   
   ![image](https://user-images.githubusercontent.com/68555817/125517945-7e13c606-5207-4b8d-95a2-9f0a43f717f4.png)
8. Populate the chan_dict dictionary found in Vars.jar
   - **do not edit chan_list and upload_playlists, they are found in FetchPlaylists.py**. add your channel(s) of choice and target playlist as such:   
   - To find your playlist id, open the playlist and copy everything after list=
   ![image](https://user-images.githubusercontent.com/68555817/125520068-250ec50e-7110-4083-9702-fb260aa9e87d.png)

  ```
   {
   "chan_dict": {
        "Channel1": "Channel1_ID",
        "...": "...",
        "ChannelN": "ChannelN_ID"
    },
   "My_Playlist": "MyPlaylist_ID",
    ...
  ```
  
9. Run FetchPlaylists.py checking afterwards that Vars.json has been properly populated with chan_list and upload_playlists
10. Run ManagePlaylist.py checking afterwards that the Add_To_Playlist.json and Archive_of_added.json files have been populated
    - These two files should be identical bar their key until you run PlaylistAdd.py when the topmost values of the list inside of Add_To_Playlist is popped.
    - Make a note of how many videos ManagePlaylist.py says it has found, Writing to a playlist uses 50 of your 10000 daily project quota meaning you can only add 200 videos a day, this will be less depending on the amount of channels you searched. 
11. Run PlaylistAdd.py This script only adds 100 videos at a time to save on quota. **Ensure you have at least 5000 quota remaining before running**
