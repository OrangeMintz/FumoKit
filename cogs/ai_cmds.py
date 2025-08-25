import discord
from discord.ext import commands
from discord import app_commands
import ollama
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Fallback prompt if missing").replace("\\n", "\n")


class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_histories = {}
        self.user_locks = {}  # one lock per user

    def get_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create a lock for a specific user."""
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
        return self.user_locks[user_id]

    @app_commands.command(name="prompt", description="Talk with Cirno")
    @app_commands.describe(prompt="Message",)
    async def ai_chat(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)
        user_id = interaction.user.id
        user_display_name = interaction.user.display_name

        # prepare user history if new
        if user_id not in self.user_histories:
            self.user_histories[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

        # add user message
        self.user_histories[user_id].append({"role": "user", "content": prompt})

        lock = self.get_lock(user_id)

        # if already busy, tell the user it's queued
        if lock.locked():
            await interaction.followup.send(
                f"❄ **Cirno** is busy with your last question... "
                f"your prompt has been **queued** ⏳"
            )

        async with lock:  # ensure prompts queue up per user
            try:
                # Always create a brand-new message for this run
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
        """Handles streaming AI response sequentially per user."""
        try:
            response_stream = ollama.chat(
                model="artifish/llama3.2-uncensored:latest",
                messages=list(self.user_histories[user_id]),  # copy history safely
                stream=True,
                options={"temperature": 0.7},
            )

            full_response = ""
            buffer = ""

            for chunk in response_stream:
                if "message" in chunk and "content" in chunk["message"]:
                    buffer += chunk["message"]["content"]

                    if len(buffer) >= 100:  # push partial updates
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

            # save AI response in history
            self.user_histories[user_id].append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            await msg.edit(content=f"❌ Something went wrong while streaming: {e}")

async def setup(bot):
    await bot.add_cog(AICommands(bot))
