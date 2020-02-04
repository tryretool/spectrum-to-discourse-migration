import pandas as pd
import requests
import json
import sys
import time
from utils import hasBody, extractText, extractTitle, formatText, DISCOURSE_API_KEY

#First system argument: Spectrum messages csv
messages = pd.read_csv(sys.argv[1])
#Second system argument: Spectrum users csv
users = pd.read_csv(sys.argv[2])
#Third system argument: topic mappings csv 
topic_mappings = pd.read_csv(sys.argv[3])

#Extract the "content" column and parse it to JSON
messages['message_content_json'] = messages.apply(lambda x: json.loads(x['content']), axis=1)

#Join messages to users to get username of the poster
posts = messages.merge(users, left_on='senderId', right_on='id', suffixes=('_posts', '_users')).copy()
#Join messages to topic_mappings to use discourse_topic_id 
posts = posts.merge(topic_mappings, left_on='threadId', right_on='topic_id').copy()

#Filter the posts dataframe for posts that haven't been created on Discourse yet
posts = posts.query("posts_posted == False").copy()

#Function for creating a single post
def postPost(api_key, username, discourse_topic_id, content_json, created_at):

    #Set the API user context as the username of whoever wrote the original topic
    headers = {
        "Api-Key": api_key,
        "Api-Username": username
    }
   
    #Define POST body (gee, a lot of the word "post" in here)
    post_body = {
        'topic_id': discourse_topic_id,
        'raw': formatText(content_json),
        'created_at': created_at
    }

    #Use for debugging if you'd like
    #print("Topic ID: "  + str(discourse_topic_id))
    
    #POST message
    r = requests.post('https://community.retool.com/posts.json',
                 data = post_body,
                 headers = headers)

    #Declare the topic_mappings dataframe as global to we can write to it
    global topic_mappings

    #If the post was successfully created, the response will have 'id' in it
    if 'id' in json.loads(r.text).keys():
        print("Post successfully added")
    #If we got rate limited, the response will have 'error_type' in it
    elif 'error_type' in json.loads(r.text).keys():
        time.sleep(60)
    #If there's a different type of error, print the response
    else:
        print(r.text)

    #Set posts_posted in topic_mappings to True
    idx = topic_mappings[topic_mappings['discourse_topic_id'] == discourse_topic_id].index[0]
    topic_mappings.loc[idx, 'posts_posted'] = True
    #Write the new information to the topic mappings CSV
    topic_mappings.to_csv('topic_mappings.csv')

##############################################################################
## Use if you had user creation errors and need to attribute posts properly ##
##############################################################################
#Because some usernames are different from Spectrum to Discourse, we need to have some error handling for when the function tries to post to the API using a username that doesn't exist in Discourse. 
#Read in a CSV of existing Discourse users
# user_list = pd.read_csv('discourse_users.csv')
# users_list = user_list['username'].tolist()
#Create a "message_username" column that fills in 'anonymous' (the admin user) if the user doesn't exist in Discourse
# posts['message_username'] = posts['username'].apply(lambda x: x if (x in users_list and ~pd.isna(x) and x != 'nan' and isinstance(x, str)) else 'anonymous')

#Apply the postPost function to every post
posts.sort_values(['discourse_topic_id','timestamp']).apply(lambda x: postPost(api_key=DISCOURSE_API_KEY,
                                                                                username=x['username'],
                                                                                discourse_topic_id=x['discourse_topic_id'],
                                                                                content_json=x['message_content_json'],
                                                                                created_at=x['timestamp']),
                                                            axis=1)