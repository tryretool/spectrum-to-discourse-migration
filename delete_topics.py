import sys
import requests
from utils import DISCOURSE_API_KEY

headers = {
    "Api-Key": DISCOURSE_API_KEY,
    "Api-Username": "anonymous"
}

#Delete topics
for i in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    r = requests.delete(url="https://community.retool.com/t/{}.json".format(i),
                        headers=headers)
    print("Topic " + str(i))