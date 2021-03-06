from pritunl.constants import *
from pritunl import settings
from pritunl import utils
from pritunl import logger

import pymongo
import os

_prefix = None
_database = None

def database_setup():
    global _prefix
    global _database

    _prefix = settings.conf.mongodb_collection_prefix or ''
    client = pymongo.MongoClient(settings.conf.mongodb_uri,
        connectTimeoutMS=MONGO_CONNECT_TIMEOUT)
    _database = client.get_default_database()

def database_clean_up():
    global _prefix
    global _database
    _prefix = None
    _database = None

def get_collection(collection):
    return getattr(_database, _prefix + collection)

def setup_cert(load_db, server_cert_path, server_key_path):
    server_cert = None
    server_key = None

    if load_db:
        settings_collection = get_collection('settings')
        doc = settings_collection.find_one({'_id': 'app'})
        if doc:
            server_cert = doc.get('server_cert')
            server_key = doc.get('server_key')

    if not server_cert or not server_key:
        logger.info('Generating setup server ssl cert', 'setup')
        utils.generate_server_cert(server_cert_path, server_key_path)
    else:
        with open(server_cert_path, 'w') as server_cert_file:
            server_cert_file.write(server_cert)
        with open(server_key_path, 'w') as server_key_file:
            os.chmod(server_key_path, 0600)
            server_key_file.write(server_key)
