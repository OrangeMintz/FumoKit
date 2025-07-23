from config.db import games_collection

class GameModel:
    @staticmethod
    def create_game(game_data: dict):
        return games_collection.insert_one(game_data)
    
    @staticmethod
    def get_game_by_title(title):
        return games_collection.find_one({"title": title})

    @staticmethod
    def update_game_by_title(title, update_data):
        return games_collection.update_one({"title": title}, {"$set": update_data})
    
    @staticmethod
    def list_game():
        return games_collection.find()
    
    @staticmethod
    def delete_game(title):
        return games_collection.delete_one({"title": title})