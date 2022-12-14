## 1. Fetch candidates from ES
## 2. get features from feature store for fetched candidates
## 3. pass the feature store data to ml model and generate predictions

import warnings
warnings.filterwarnings("ignore")
import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(os.getcwd()).parent))
sys.path.append(str(Path(os.getcwd())) + "/retrieval")
sys.path.append(str(Path(os.getcwd())) + "/ranking")
sys.path.append(str(Path(os.getcwd())))

from retrieval.es_queries.retrieve_candidates import CandidateRetrieval
from retrieval.src.get_feat_from_fs import GetFeaturesFromFS
from ranking.inference import GetRecommendations


from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time
# from utils import get_logger
from logzero import logger

candidate_retrieval = CandidateRetrieval()
get_feature_from_fs = GetFeaturesFromFS()
reco = GetRecommendations()

app = FastAPI()

class recommendations_schema(BaseModel):
    user_id : str
    user_country: str

@app.get("/")
def read_root():
    """
    ** Description: ** <em> It returns a dictionary with a single key, "Welcome to AI-Internal Recommendation system" </em>

    Returns:
        (dict): A dictionary with a string as the value.
    """
    return {"Welcome to AI-Internal Recommendation system"}

################################################################
######################## API endpoints #########################
################################################################
@app.post("/get_recommendations/")
async def fetch_recommendations(record: recommendations_schema):
    """
    ** Description: ** <em> Given a user record, retrieve a candidate set of assets, fetch features from the feature store, \
    and generate recommendations </em>
    
    Args:
        record (dict): This is the input data that we will be passing to the function

    Returns:
        (list): A list of recommendations
    """
    start_time = time.time()
    record = record.dict()
    
    ## 1. Retrieve candidate set
    candidate_set = candidate_retrieval.es_retrieve_candidates(record["user_country"], record["user_id"],)
    logger.info(f"candidate set: {candidate_set}")
    logger.info(f"time taken to retrieve candidates {time.time() - start_time}")
    
    ####### UNCOMMENT FOR LOCAL TESTING
    # candidate_set = ["96245856-cd68-43b4-a7ae-ec53cc109d9c",
    #                  "dec54659-6557-4453-9978-19249bb3593f",
    #                  "07964421-f8a2-48d9-a340-48beafd73230",
    #                  "c94b5991-79c3-42b5-9c7a-390a19c26b4e",
    #                  "a83f9f6b-2b5f-40ec-a7e8-5fe5488b64b3",
    #                  "d37d89ce-9d02-44aa-bcbd-9757ae2e4e45",
    #                  "8412284f-0f94-4323-ad54-c37a20044f22",
    #                  "c0dc1e26-8eaa-4843-b019-727b3745c23e",
    #                  "5f178248-4528-41c9-a670-d590a974c77c",
    #                  "e9b23afc-f71b-4ec9-aacc-e81a5d29dbc2",
    #                  "34019e21-3b84-4b99-a8ea-8b7c130a2dbb",
    #                  "77793676-88b1-4b30-b759-5323df7d6d2a",
    #                  "b56b2a3c-7bb0-420a-91ab-044240536adb",
    #                  "876b8229-a49c-423b-9c87-47d544c2eb0b",
    #                  "d2b16ac3-0f6d-4d8d-ad82-3378a4748d26",
    #                  "5fedd89a-b764-4795-8203-89feada7cd3f",
    #                  "bb4b4f9b-e80d-4228-965f-0d69e21a3183",
    #                  "4d717a98-b11e-4db2-814e-07ea2d6f52ce",
    #                  "8ca9da2f-1ba7-4812-81ac-6e350f665432",
    #                  "57920579-4aef-40ef-8b11-ab4d81888058",
    #                  "529853da-920f-4215-8f4f-69e10130b1f8",
    #                  "d1a921b2-c65f-43dc-9185-b2f799093297"]

    # sample_users  = ["23006868","37910338","38097984","30946863","38044772",
    #                  "24314889","38050694","38138978","25898093","26300013",
    #                  "38091509","27981115","35813408","32339465","31512640",
    #                  "20498996","37901613","16803332","38000838","11097832",
    #                  "37377740","37922402","38126464","38092257","36988243",
    #                  "35726426","32252684","17684453","38063573","38071530",
    #                  "19331476","31978224","35847633","20249860","37219883",
    #                  "31253160","38067870","36503606"]

    #### Substitute any one user id from the list above 
    # record["user_id"] = "36503606"
    #         OR
    # record["user_id"] = ""

    ## 2. Fetch data from feature store 
    fs_time = time.time()   
    if record["user_id"] != "":
        _ = get_feature_from_fs.get_asset_features_from_fs(candidate_list=candidate_set)
        model_df = get_feature_from_fs.get_user_features_from_fs(record['user_id'])
        logger.info(model_df)
    else:
        model_df = get_feature_from_fs.get_asset_features_from_fs(candidate_list=candidate_set)
        logger.info(model_df)
    logger.info(f"time taken to extract features from feature store {time.time() - fs_time}")
    
    ## 3. Generate Recommendation (Ranking)
    ranking_time = time.time()   
    recommendations = reco.generate_recommendations(model_df)

    logger.info(recommendations)
    logger.info(f"time taken Generate recommendations {time.time() - ranking_time}")  
    logger.info(f"API response time {time.time() - start_time}")
    
    return recommendations



if __name__ == "__main__":
    uvicorn.run("internal_reco_api:app", host="0.0.0.0", port=8000, log_level="info")
