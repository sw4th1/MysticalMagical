import requests
import json

payload = { 'type': 'data', 
            'payload': {
               'user_id': '10', 
               'tracks': {
                    "1ZHvGQZNz6HLbxhAtu7pin": {
                    "name": "Ma Meilleure Ennemie ft. Coldplay",
                    "uri": "spotify:track:1ZHvGQZNz6HLbxhAtu7pin",
                    "image_url": "https://i.scdn.co/image/ab67616d00001e02183fc5de03ccc82fb1154774"
                    }
               }
            }
        }
        
# payload = { 'type': 'remove', 
#             'payload': "10"
#             }

# response = requests.post('http://localhost:8080', data=json.dumps(payload))
response = requests.post('https://801f-2a09-bac5-7a4b-1cd2-00-2df-e5.ngrok-free.app', data=json.dumps(payload))
# response = requests.post('https://hot-mostly-hedgehog.ngrok-free.app', data=json.dumps(payload))
print(response.text)