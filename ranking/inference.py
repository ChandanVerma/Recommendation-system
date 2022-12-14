import warnings
warnings.filterwarnings("ignore")
import pickle
import xgboost as xgb 
# from ranking.src.utils import load_config

from logzero import logger
import traceback
import pandas as pd
import yaml

def load_config(file_path):
    """
    ** Description: ** <em> It opens the file at the given path, reads the contents, and parses the contents as a YAML file </em>
    
    Args:
        file_path (str): The path to the YAML file
    Returns:
        (dict): A dictionary
    """
    with open(file_path, 'r') as f:
        cfg = yaml.safe_load(f)
    return cfg

config = load_config("config.yml")

class GetRecommendations:
    def __init__(self):
        """
        ** Description: ** <em> It loads the model and the cold start model from the model path and model name specified in the
        config file </em>
        """
        try:
            logger.info("Loading Recommendation Model")
            self.model = pickle.load(open(config["model_path"] + config["model_name"], "rb"))
            logger.info("ML model successfully loaded")
            logger.info("Loading cold start Model")
            self.cold_start_model = pickle.load(open(config["model_path"] + config["cold_start_model_name"], "rb"))
            logger.info("ML model successfully loaded")
            self.prediction_columns = config["prediction_features"]
            self.cold_start_columns = config["cold_start_features"]
        except:
            logger.info(f"Couldnt load Recommendation model: {traceback.print_exc()}" )
            
    def generate_recommendations(self, candidate_set):
        """
        ** Description: ** <em> If the user has a user vector, then we use the trained model to predict the scores for the
        candidate set. If the user doesn't have a user vector, then we use the cold start model to
        predict the scores for the candidate set </em>
        
        Args:
            candidate_set (pd.DataFrame): This is the set of items that we want to generate recommendations for
        Returns:
            (list): a list of 10 lomotif_ids to be recommended in sorted probability order (e.g. highest probability lomotif_id will be ranked at the top) 
        """
        try:
            logger.info("Making predictions")
            if "user_vv" in candidate_set.columns:
                logger.info("using full model")
                candidate_set = candidate_set[["lomotif_id"] + self.prediction_columns]
                candidate_set[self.prediction_columns] = candidate_set[self.prediction_columns].astype("float")
                dtest = xgb.DMatrix(data=candidate_set[self.prediction_columns], enable_categorical = True)
                self.test_res = self.model.predict(dtest)
                candidate_set["predictions"] = self.test_res
                # logger.info(candidate_set[["lomotif_id", "predictions"]].dropna().sort_values("predictions", ascending = False).reset_index(drop = True))
                recommendations = candidate_set[["lomotif_id", "predictions"]].dropna().sort_values("predictions", ascending = False).reset_index(drop = True)["lomotif_id"][:10].tolist()
                return recommendations
            else:
                logger.info("using coldstart model")
                candidate_set[self.cold_start_columns] = candidate_set[self.cold_start_columns].astype("float")
                dtest = xgb.DMatrix(data=candidate_set[self.cold_start_columns], enable_categorical = True)
                self.test_res = self.cold_start_model.predict(dtest)
                candidate_set["predictions"] = self.test_res
                recommendations = candidate_set[["lomotif_id", "predictions"]].dropna().sort_values("predictions", ascending = False).reset_index(drop = True)["lomotif_id"][:10].tolist()
                return recommendations
        except:
            logger.info(f"Couldnt Generate recommendations: {traceback.print_exc()}" )
            

# if __name__ == "__main__":
#     # data = cd.read_parquet(config["preprocessed_data_path"] + config["preprocessed_file_name"], engine= "parquet")
#     data = pd.read_parquet(config["preprocessed_file_name"])
#     data.head()
#     data = data.sample(n = 1000)
#     data = data[["lomotif_id"] + config["cold_start_features"]]
#     reco = GetRecommendations()
#     pred = reco.generate_recommendations(data)
#     print(pred)
#     # reco.calulate_inference_performance()
