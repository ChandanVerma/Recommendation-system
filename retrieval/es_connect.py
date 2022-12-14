import warnings
warnings.filterwarnings(action = 'ignore')
import os
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

from dotenv import load_dotenv
load_dotenv("./.env")

YOUR_ACCESS_KEY = os.environ["AWS_ACCESS_KEY_ID"]
YOUR_SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
REGION = os.environ["AWS_REGION"]

ES_HOST = os.environ["ES_HOST"]
ES_PORT = int(os.environ["ES_PORT"])

awsauth = AWS4Auth(YOUR_ACCESS_KEY, YOUR_SECRET_KEY, REGION, 'es')

es = OpenSearch(
    hosts = [{'host': ES_HOST, 'port': ES_PORT}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth=awsauth,
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl = True,
    verify_certs = True,
    ssl_assert_hostname = False,
    ssl_show_warn = False,
    # ca_certs = ca_certs_path,
    connection_class=RequestsHttpConnection
)
