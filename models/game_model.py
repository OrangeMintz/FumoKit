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
    
    @staticmethod
    def get_game_by_title(title):
        return games_collection.find_one({"title": title})

    @staticmethod
    def update_game_by_title(title, update_data):
        return games_collection.update_one({"title": title}, {"$set": update_data})
