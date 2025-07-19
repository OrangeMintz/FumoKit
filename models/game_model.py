from config.db import games_collection

class GameModel:
    @staticmethod
    def create_game(author, author_id, title, desc, vers, size, date, link, image_url):
        game_data = {
            "author": author,
            "author_id": author_id,
            "title": title,
            "description": desc,
            "version": vers,
            "size": size,
            "date": date,
            "link": link,
            "image_url": image_url
        }
        return games_collection.insert_one(game_data)

# config/db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODb")
client = MongoClient(MONGO_URI)
db = client["discord_bot"]
games_collection = db["games"]
