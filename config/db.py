from pymongo import MongoClient

MONGO_URI  = "mongodb+srv://priyawork2989:%3Cfriya%402989%3E@cluster0.gjsjyhj.mongodb.net/9"

conn = MongoClient(MONGO_URI)
def get_user_collection():
    return conn["users"]