import discord
from discord.ext import commands
from discord import app_commands
import ollama
import asyncio
import os
from dotenv import load_dotenv
from models.ai_model import AIModel

load_dotenv()

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Fallback prompt if missing").replace("\\n", "\n")
C_SYSTEM_PROMPT = os.getenv("C_SYSTEM_PROMPT", "Fallback prompt if missing").replace("\\n", "\n")
AI_MODEL = os.getenv("AI_MODEL", "Fallback prompt if missing")
CREATOR_ID = int(os.getenv("CREATOR_ID", 0))

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_histories = {}
        self.user_locks = {}

    def get_lock(self, user_id: int) -> asyncio.Lock:
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
        return self.user_locks[user_id]
    
    async def load_user_history(self, user_id: int):
        system_prompt = SYSTEM_PROMPT
        if user_id == CREATOR_ID:
            system_prompt += C_SYSTEM_PROMPT
        
        # Load last N messages from DB into memory
        history = [{"role": "system", "content": system_prompt}]
        docs = AIModel.get_history(user_id, limit=10)
        for doc in docs:
            history.append({"role": "user", "content": doc["prompt"]})
            history.append({"role": "assistant", "content": doc["response"]})
        self.user_histories[user_id] = history
        return history

    @app_commands.command(name="prompt", description="Talk with Cirno")
    @app_commands.describe(prompt="Message")

    async def ai_chat(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)
        user_id = interaction.user.id
        user_display_name = interaction.user.display_name

        # Load from DB if user history not in memory
        if user_id not in self.user_histories:
            await self.load_user_history(user_id)

        # Add new user message
        self.user_histories[user_id].append({"role": "user", "content": prompt})

        lock = self.get_lock(user_id)

        if lock.locked():
            await interaction.followup.send(
                f"❄ **Cirno** is busy with your last question... "
                f"your prompt has been **queued** \u2705"
            )

        async with lock:
            try:
                msg = await interaction.followup.send(
                    f"**{user_display_name}**: {prompt}\n"
                    f"**Cirno**: <:cirnofumo:1260121161149186049> Thinking..."
                )
                await self.stream_response(user_id, prompt, user_display_name, msg)
            except Exception as e:
                await interaction.followup.send(
                    f"❌ Something went wrong: {e}", ephemeral=True
                )

    async def stream_response(self, user_id, prompt, user_display_name, msg):
        try:
            response_stream = ollama.chat(
                model=AI_MODEL,
                messages=list(self.user_histories[user_id]),
                stream=True,
                options={"temperature": 0.7},
            )
            full_response = ""
            buffer = ""
            for chunk in response_stream:
                if "message" in chunk and "content" in chunk["message"]:
                    buffer += chunk["message"]["content"]
                    if len(buffer) >= 100:
                        full_response += buffer
                        await msg.edit(
                            content=f"**{user_display_name}**: {prompt}\n"
                                    f"**Cirno**: {full_response[:2000]}"
                        )
                        buffer = ""
            if buffer:
                full_response += buffer
                await msg.edit(
                    content=f"**{user_display_name}**: {prompt}\n"
                            f"**Cirno**: {full_response[:2000]}"
                )
            # Save to DB
            AIModel.save_history(user_id, prompt, full_response)

        except Exception as e:
            await msg.edit(
                content=f"❌ Cirno tried to think really hard, "
                        f"but she found herself dumbfounded 🔌 {e}"
            )

async def setup(bot):
    await bot.add_cog(AICommands(bot))