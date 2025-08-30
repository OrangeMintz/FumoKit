from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)

db = client["discord_bot"]
games_collection = db["games"]
ai_history_collection = db["user_history"]