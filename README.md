# AI Model Based Recommendations
This repo generates recommendations using recommendation systems.

# Set-up .env file
There needs to be a `.env` file with following parameters.
```
AWS_ACCESS_KEY_ID=YOUR AWS ACCESS KEY
AWS_SECRET_ACCESS_KEY=YOUR AWS SECRET KEY
AWS_REGION=us-east-2

ES_HOST = YOUR ES HOST
ES_PORT = YOUR ES PORT

REDIS_IP = YOUR REDIS URL
REDIS_PORT = 6379
ASSET_FS_DB = 1
USER_FS_DB = 1

CANDIDATES_TO_RETRIEVE = 1000
```

# Instructions (Docker)
1) Ensure there are environment variables or `.env` file, see section above for environment variables.
```
docker-compose build
docker-compose up
```

## Local Testing
```
1. pip install -r requirements.txt
2. open internal_reco_api.py in code editor or notepad and uncomment line 73-139
3. we can substitute any sample user from 141-148 in 151 
4. uncomment line 151 if using with user_id else for no user_id uncomment 153
5. python internal_reco_api.py

```

# API details
After successfully building up the docker container, the following is the API details to generate recommendations

```
http://0.0.0.0:8000/get_recommendations/
```

payload:
```
{
    "user_id": "38073944",
    "user_country": "BR"
}
```

Response: 
```
[
    "9a2e0855-ff1e-4365-bdb4-ef4181b05089",
    "d852c146-b8eb-4d67-bcbc-e9d8bd44587c",
    "b3ba7b9e-6bef-4a9e-8a80-89d84a689266",
    "9b6c21bf-70be-4143-a5ac-ffbd79395835",
    "276fce68-8b2e-40ee-b291-8ee27f33c41f",
    "b93f7887-abbd-44c3-9d8a-5571c0ba8dd0",
    "bc7ef309-91fe-492a-aa01-6784fb7f676f",
    "75269e2d-2817-4f44-ba81-27389570df18",
    "3436a660-6bfe-49b3-be4e-07a9fe349262",
    "15f29d1b-7661-4c8c-91da-3d7c7086b319"
]
```

The API returns a list of video ids that needs to be recommended sorted on probability score. i.e. videos id higher on the list has the higher probability of watch completion

The backend team needs to filter this list based on user_blacklist from the ES index and make recommendations to make sure that no same videos is recommended to user again and again

### NOTE: This repo assumes that ES DB and Redis Feature store is up and running with the folowing infomation

#### 1. ES 
##### Asset Index
``` 
video_id
creation_date
production_country
moderation_status
primary_category
secondary_category
```
##### User Index:
```
user_id
user_country
user_blacklist
```

#### 2. Redis Feature Store
##### Asset feature store
```
{'prob_pc_1_watch': '0.176717412', 'video_vv': '2', 'prob_asset_watch': '0.161405162'}
```

##### User feature store
```
{'prob_user_watch': '0.165255043', 'user_vv': '62'}
```

# Technical documentation
```
pip install -r mkdocs_requirements.txt
mkdocs serve
```

# Todo
1. Adding additional user and asset level features in feature store
2. Pytest
