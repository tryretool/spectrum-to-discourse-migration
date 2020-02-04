import pandas as pd
import requests
import json
import sys
from utils import DISCOURSE_API_KEY, TEAM_USERNAMES, TEAM_USERNAMES_SMALL

users = pd.read_csv(sys.argv[1])

#If username is null, add a temporary one (their email address)
#users = users[(pd.isna(users['username']) == True) & (pd.isna(users['email']) == False)]
#users['temp_username'] = users.apply(lambda x: str(x['email']).split('@')[0], axis=1)

if len(sys.argv) > 2:
    if sys.argv[2] == 'team':
        users = users[users['username'].isin(TEAM_USERNAMES)].copy()
    elif sys.argv[2] == 'team-small':
        users = users[users['username'].isin(TEAM_USERNAMES_SMALL)].copy()

headers = {
    "Api-Key": DISCOURSE_API_KEY,
    "Api-Username": "anonymous"
}

url = 'https://community.retool.com/users'

def createUser(name, email, password, username, headers):

    body = {
        'name': name,
        'email': email,
        'password': password,
        'username': username,
        'active': 'true',
        'approved': 'true'
    }

    r = requests.post(url='https://community.retool.com/users', 
                      data = body, 
                      headers = headers)

    print(r.text)                 
    return r.text

users.apply(lambda x: createUser(name=x['name'], 
                                        email=x['email'], 
                                        password='whatevertemp', 
                                        username=x['username'], 
                                        headers=headers),
            axis=1)