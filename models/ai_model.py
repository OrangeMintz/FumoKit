from config.db import ai_history_collection

class AIModel:
    @staticmethod
    def save_history(user_id: int, prompt: str, response: str):
        """Insert a conversation turn into MongoDB"""
        return ai_history_collection.insert_one({
            "user_id": user_id,
            "prompt": prompt,
            "response": response
        })

    @staticmethod
    def get_history(user_id: int, limit: int = 50):
        """Retrieve the last N conversation turns for a user"""
        cursor = (
            ai_history_collection.find({"user_id": user_id})
            .sort("_id", -1)  # newest first
            .limit(limit)
        )
        return list(cursor)[::-1]  # reverse so oldest comes first
