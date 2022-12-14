import warnings
warnings.filterwarnings("ignore")
import os
import redis
import pandas as pd
from logzero import logger
import traceback
from dotenv import load_dotenv

load_dotenv("./.env")
KEY_PREFIX = "recommendations_preprocessing"

class GetFeaturesFromFS:
    def __init__(self) -> None:
        """
        ** Description: ** <em> The function tries to connect to the feature store and if it fails, it logs the exception </em>
        """
        try:
            logger.info("Connecting to feature store")
            self.asset_fs = redis.StrictRedis(host=os.environ["REDIS_IP"], 
                                              port=os.environ["REDIS_PORT"], 
                                              db=os.environ["ASSET_FS_DB"], 
                                              decode_responses=True)
            self.user_fs = redis.StrictRedis(host=os.environ["REDIS_IP"], 
                                             port=os.environ["REDIS_PORT"], 
                                             db=os.environ["USER_FS_DB"], 
                                             decode_responses=True)
            self.asset_pipe = self.asset_fs.pipeline()
            if self.asset_fs.ping() and self.user_fs.ping():
                logger.info("Connection to feature store successfully established !!!")
            else:
                logger.info("Couldnt connect to Redis !!!")
        except:
            logger.info(f"Got the following exception: {traceback.format_exc()}")    

    def get_asset_features_from_fs(self, candidate_list):
        """ ** Description: ** <em> This function fetches the lomotif level features from the feature store </em>

        Args:
            candidate_list (list): list of lomotif ids generated from (ES DB) retrieval step

        Returns:
            (pd.DataFrame): returns only asset level features from feature store
        """
        try:
            logger.info("Retrieving asset feature from feature store")
            for item in candidate_list:
                asset_key = KEY_PREFIX + "_asset:" + item
                self.asset_pipe.hgetall(asset_key)
            asset_data = self.asset_pipe.execute()
            self.model_df = pd.DataFrame.from_records(asset_data)           
            self.model_df["lomotif_id"] = candidate_list
            self.model_df.dropna(inplace=True)
            return self.model_df
        except: 
            logger.info(f"Got the following exception: {traceback.format_exc()}")

    def get_user_features_from_fs(self, user_id=None):
        """ ** Description: ** <em> This function fetches the user level features from the feature store and aggregates it with asset (lomotif) level features and makes it consumable for the recommendations model </em>

        Args:
            user_id (str): user_id for which the feature needs to be retreived from the feature store

        Returns:
            (pd.DataFrame): if user details exists returns combined (asset + user) features \
            else returns only asset level features from feature store
        """
        try:
            if user_id == None:
                return self.model_df
            
            user_key = KEY_PREFIX + "_user:" + user_id
            print(user_key)
            user_data = self.user_fs.hgetall(user_key)
            logger.info(user_data)
            # If the user_data is empty, then it will return the model_df.
            if len(user_data) == 0:
                logger.warn("No user details found in feature store, returning only lomotif level info !!!")
                return self.model_df
            else:
                logger.info("Retrieving user feature from feature store")
                user_data = [user_data] * len(self.model_df)
                user_df = pd.DataFrame.from_records(user_data)
                model_data = pd.concat([self.model_df, user_df], axis = 1)
                return model_data
        except:
            logger.info(f"Got the following exception: {traceback.format_exc()}")
