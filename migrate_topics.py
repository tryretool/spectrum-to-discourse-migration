import pandas as pd
import requests
import json
import sys
import time
from utils import hasBody, extractText, extractTitle, formatText, DISCOURSE_API_KEY, TEAM_USERNAMES, TEAM_USERNAMES_SMALL

#First system argument: Spectrum threads csv
threads = pd.read_csv(sys.argv[1])
#Second system argument: Spectrum users csv
users = pd.read_csv(sys.argv[2])
#Third system argument: topic mappings csv (init to empty)
topic_mappings = pd.read_csv(sys.argv[3])

#HTTP headers: default user to admin user ('anonymous')
headers = {
    "Api-Key": DISCOURSE_API_KEY,
    "Api-Username": "anonymous"
}

#Dict that maps the Spectrum RethinkDB channelId to the new Discourse channel name
channel_mappings = {
    '85cf0f33-a1b2-46fc-9c55-0f35ef7eb555': 'Support',
    '4ccd36fc-a263-45ec-9a1c-d350f1d4f4ab': 'Feature Requests',
    'a1f2c027-db49-4c74-8abc-b4f76bee2a3d': 'Show and Tell',
    'eada7c39-f751-433a-867e-3fa467209169': 'None',
    '6b05daef-749c-41f6-b39d-ad799c27b5cb': 'None'
}

#Apply the channel mappings to the threads data so we know which Discourse channel to post them to
threads['channel_name'] = threads.apply(lambda x: channel_mappings[x['channelId']], axis=1)

#Filter out threads in irrelevant channels
threads = threads[threads['channel_name'].isin(['Support', 'Feature Requests', 'Show and Tell'])]

#Create an intermediate content JSON column for easier parsing
threads['content_json'] = threads.apply(lambda x: json.loads(x['content']), axis=1)

#Filter threads for threads with a body
threads['has_body'] = threads.apply(hasBody, axis=1)
threads = threads.query("has_body == 1").copy().reset_index(drop=True)

#Extract title
threads['title'] = threads.apply(extractTitle, axis=1)

#Function to get category IDs from Discourse and generate a mapping dictionary
def generateCategoriesDict():
    headers['Api-Username'] = 'anonymous'
    r = requests.get('https://community.retool.com/categories.json', headers = headers)
    categories_dict = {}
    categories = json.loads(r.text)['category_list']['categories']
    for category in categories:
        categories_dict[category['name']] = category['id']
    return categories_dict

def postTopic(title, content_json, channel, created_at, username, api_key, topic_id):
    
    #Set the API user context as the username of whoever wrote the original topic
    headers = {
        "Api-Key": api_key,
        "Api-Username": username
    }
    
    #Set the POST body 
    body = {
        'title': title,
        'raw': formatText(content_json),
        'category': channel,
        'created_at': created_at
    }
    
    #Make the API call to the posts endpoint
    r = requests.post(url='https://community.retool.com/posts.json',
                        data = body,
                        headers = headers)
    
    #Declare the topic_mappings dataframe as global to we can write to it
    global topic_mappings

    #If the response object has a 'topic_id' key, it was successful; append a row to topic mappings
    try:
        discourse_topic_id = json.loads(r.text)['topic_id']
        #Use for debugging
        # print("Topic ID: " + str(discourse_topic_id))
        topic_mappings = topic_mappings.append({'topic_id': topic_id, 
                                                'discourse_topic_id': discourse_topic_id,
                                                'posts_posted': False}, 
                                            ignore_index=True)
    #If the request wasn't successful
    except:
        #If it's a rate limit error, write the new data to the topic mappings csv and get outta here
        try:
            if r['error_type']  == 'rate_limit':
                topic_mappings.to_csv('topic_mappings.csv')
                raise
        #If it's another kind of error, let it go and print the response text
        except:
            print(json.loads(r.text))


#Create merged dataframe so topics have usernames
topics = threads.merge(users[['id', 'name', 'username', 'email']], left_on='creatorId', right_on='id', suffixes=('_topics', '_users'))

categories_dict = generateCategoriesDict()

##############################################################################
## Use if you had user creation errors and need to attribute posts properly ##
##############################################################################
#Because some usernames are different from Spectrum to Discourse, we need to have some error handling for when the function tries to post to the API using a username that doesn't exist in Discourse. 
#Read in a CSV of existing Discourse users
# user_list = pd.read_csv('discourse_users.csv')
# users_list = user_list['username'].tolist()
# topics['topic_username'] = topics['username'].apply(lambda x: x if (x in users_list and ~pd.isna(x) and x != 'nan' and isinstance(x, str)) else 'anonymous')

#Apply postTopic function to each Spectrum thread
topics.apply(lambda x: postTopic(title=x['title'],
                                    content_json=x['content_json'],
                                    channel=categories_dict[x['channel_name']],
                                    created_at=x['createdAt'],
                                    username=x['topic_username'],
                                    api_key=DISCOURSE_API_KEY, 
                                    topic_id=x['id_topics']),
                axis=1)

#Write topic ID mapping to CSV
topic_mappings.to_csv('topic_mappings.csv')