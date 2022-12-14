import warnings
warnings.filterwarnings("ignore")
import os
import random
import traceback
import sys
import time
from pathlib import Path
import redis

sys.path.append(str(Path(os.getcwd()).parent))
sys.path.append(str(Path(os.getcwd())) + "/retrieval")
sys.path.append(str(Path(os.getcwd())) + "/ranking")
sys.path.append(str(Path(os.getcwd())))

from logzero import logger
from utils import load_config

from dotenv import load_dotenv
KEY_PREFIX = "recommendations_preprocessing"

load_dotenv("./.env")

class CandidateRetrieval:
    def __init__(self) -> None:
        """
        ** Description: ** <em> The function loads the config file, then tries to connect to the OpenSearch database. If it
        can't connect, it logs the error </em>
        """
        self.config = load_config("config.yml")
        try:
            from retrieval.es_connect import es
            self.es = es
            if self.es.ping():
                logger.info(f"Successfully connected to OpenSeach DB: {es}")
            else:
                logger.info("Could not connect to Opensearch")
        except:
            logger.info(f"Could not connect to Opensearch: {traceback.format_exc()}")
            # file_logger.info(f"{traceback.print_exception()}")  
    
    def search_sample_asset(self):
        """ ** Description: ** <em> This function returns a sample set from the ES index </em> 

        Returns:
            (dict): sample data in dict format
        """
        query = {
      	    "query": {
      	    	"query_string": {
      	    		"query": "*"
      	    	    }
      	        },
      	    "size": 10,
      	    "from": 0,
      	    "sort": []
            }
        resp = self.es.search(index = self.config["ES_INDEX_NAME"], body=query)
        return resp['hits']['hits']

    def get_blacklist_assets_list(self, user_id):
        """
        ** Description: ** <em> It takes in a user_id and returns a list of assets that the user has blacklisted </em>
        
        Args:
            user_id (str): The user id of the user whose blacklist assets list is to be fetched
        
        Returns: 
            (list): A list of assets that is blacklisted for the user.
        """
        query =  {
            "_source": {
            "include" :['user_blacklist']
          },
            "query" :{
                "match_phrase":{
                    "user_id" :{
                        "query" : user_id
                    }
                }
            }
        }
        resp = self.es.search(index = self.config["ES_USER_INDEX_NAME"], body= query)
        print(resp)
        try:
            resp = resp['hits']['hits'][0]['_source']['user_blacklist']
            return resp
        except:
            return [] 

    def es_retrieve_candidates(self, user_country, user_id = None):
        """ ** Description: ** <em> This function returns a set of lomotif ids that will be passed \
        on to the ML model for ranking purpose </em>

        Args:
            user_country (str): The country user belongs to in ISO 2 format e.g. (united states = "US", france = "FR")

        Returns:
            (list): A list of lomotif ids based on the country user belongs to
        """
        if user_id is not None:
            assets = self.get_blacklist_assets_list(user_id)
        else: 
            assets = []

        db_record_count_query =  {
            "query" :{
                "match":{
                    "production_country" : user_country
                }
            }
        }

        normal_query =  {
            "size": 1000,
            "query": { 
            "bool": { 
              "must": [
                { "match": {"production_country" : user_country}},
              ],
            #   "must_not" :[
            #     {
            #       "terms": {"lomotif_id.keyword" : assets }
            #     }
            #   ],
              "filter": [ 
                { "term":  { "moderation_status.keyword": "ACCEPT" }},
              ]
            }
          },
          "sort" :{
                    "creation_date" :{"order": "desc"}
                        }
        }
        logger.info("Retrieving candidate list from ES Index")
        rec_count = self.es.count(index=self.config["ES_INDEX_NAME"], body=db_record_count_query)["count"]
        print(rec_count)
        if rec_count == 0:
            logger.info("no records in ES for given country")
            return "no lomotif in ES DB for given country"
        try:          
            if rec_count >= 500: 
                resp = self.es.search(index = self.config["ES_INDEX_NAME"], body= normal_query)
                resp = resp['hits']['hits']
                # print(resp)
                # assetList = [resp[e]['_source']["lomotif_id"] for e in range(len(resp))]
                assetList = [resp[e]["_id"] for e in range(len(resp))]
                # assetList = list(set(assetList) - set(assets))
                candidate_list = random.sample(assetList, 100)
                logger.info("Candidate list successfully retrieved")
                return candidate_list
            elif (rec_count < 1000)  &  (rec_count > 0):
                less_record_query = {
                    "size": rec_count,
                        "query": { 
                            "bool": { 
                              "must": [
                                { "match": {"production_country" : user_country}},
                              ],
                            #   "must_not" :[
                            #     {
                            #       "terms": {"lomotif_id.keyword" : assets }
                            #     }
                            #   ],
                              "filter": [ 
                                { "term":  { "moderation_status.keyword": "ACCEPT" }},
                              ]
                            }
                          },
                          "sort" :{
                                    "creation_date" :{"order": "desc"}
                                        }
                        }
                resp = self.es.search(index = self.config["ES_INDEX_NAME"], body= less_record_query)
                resp = resp['hits']['hits']
                # print(len(resp))
                # assetList = [resp[e]['_source']["lomotif_id"] for e in range(len(resp))]
                assetList = [resp[e]["_id"] for e in range(len(resp))]
                # assetList = list(set(assetList) - set(assets))
                # print(assetList)
                # sample_count = int(0.5 * float(rec_count))
                candidate_list = random.sample(assetList, int(0.3 * float(rec_count)))
                logger.info("Candidate list successfully retrieved")
                return candidate_list
        except:
            logger.info(f"Got the following exception: {traceback.format_exc()}")
            # file_logger.info(f"{traceback.print_exc()}") 
        # return resp

# search_sample_asset()

# # if __name__ == "__main__":
#     asset_fs = redis.StrictRedis(host=os.environ.get("REDIS_IP"), 
#                                  port=os.environ.get("REDIS_PORT"), 
#                                  db=os.environ.get("ASSET_FS_DB"), 
#                                  decode_responses=True)
# #                                  asset_fs.ping()
# # #     candidate_retrieval = CandidateRetrieval()
# # #     reco = GetRecommendations()
# # #     ## 1. Retrieve candidate set
# # #     # start_time = time.time()


# # #     can_list = candidate_retrieval.es_retrieve_candidates(user_country="IN")
# # #     len(can_list)
# # #     ## 2. Fetch data from feature store
# # for candidate in candidate_list:
# #     asset_key = KEY_PREFIX + "_asset:" + candidate
# #     asset_key = KEY_PREFIX + "_asset:"
#     asset_fs.hgetall("recommendations_preprocessing_user:23006868")
#     for key in asset_fs.scan_iter("recommendations_preprocessing_user:*"):
#         print(key)
#         # break
# #     # delete the key
# #     ## 3. Generate Recommendation (Ranking)   
# #     pred = reco.make_predictions(model_df)
# #     # pred[pred["ASSET_ID"] == "1e0cb829-4143-4a80-9c56-8c5ff794c864"]
# #     recommendations = reco.generate_recommendations()
# #     # print(pred[pred["ASSET_ID"].isin(list(recommendations.keys())[:10])][['TE_PC_1_H_Categorify_target', 'CE_ASSET_ID_H',
# #     #    'TE_ASSET_ID_H_Categorify_target', 'ASSET_ID', 'predictions',]])
# #     print(list(recommendations.keys())[:10])
# #     print("Time taken to generate recommendation", time.time() - start_time)
