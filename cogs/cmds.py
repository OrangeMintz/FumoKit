import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from models.game_model import GameModel
from datetime import datetime, timezone

class AllBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 1395461570972225537 is a test channel
        # 1255987489907277896 is the channel for game submissions
        self.gaming_channel = [1256421833884958800, 903261559181160478, 1255987489907277896, 1395461570972225537]
        self.gaming_role = ["Admin", "Moderator", "Pirata"]

    @app_commands.command(name="submitgame", description="Submit or update a game")
    @app_commands.describe(
        title="Title",
        description="Description",
        version="Version",
        size="Size",
        date="Release Date",
        link="Download link",
        image_url="Image URL"
    )
    async def submitgame(self, interaction: discord.Interaction, title: str, description: str = None, version: str = None, size: str = None, date: str = None, link: str = None, image_url: str = None):
        try:
            
            member = interaction.user
            if not any(role.name in self.gaming_role for role in member.roles):
                await interaction.response.send_message(":x: You do not have permission to submit games.",
                    ephemeral=True)
                return
            
            if interaction.channel_id not in self.gaming_channel:
                await interaction.response.send_message("Please use this command in the designated game channels only.", ephemeral=True)
                return

            now = datetime.now(timezone.utc)
            existing_game = GameModel.get_game_by_title(title)

            if existing_game: 
                update_fields = {
                    "author": str(interaction.user),
                    "author_id": str(interaction.user.id),
                    "updated_at": now
                }
                if description: update_fields["description"] = description
                if version: update_fields["version"] = version
                if size: update_fields["size"] = size
                if date: update_fields["date"] = date
                if link: update_fields["link"] = link
                if image_url: update_fields["image_url"] = image_url
                
                GameModel.update_game_by_title(title, update_fields)
                action = 'updated'                
                
            else:
                GameModel.create_game({
                    "author": str(interaction.user),
                    "author_id": str(interaction.user.id),
                    "title": title,
                    "description": description,
                    "version": version,
                    "size": size,
                    "date": date,
                    "link": link,
                    "image_url": image_url,
                    "created_at": now,
                    "updated_at": now
                })
                action = 'posted'

            embed = discord.Embed(
            title=title,
            description=description or existing_game.get("description", ""),
            url=link or existing_game.get("link", ""),
            color=discord.Color.random()
            )
            embed.set_thumbnail(url=image_url or existing_game.get("image_url", ""))
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.add_field(name=":tools: Version", value=version or existing_game.get("version", "N/A"), inline=True)
            embed.add_field(name=":floppy_disk: Size", value=size or existing_game.get("size", "N/A"), inline=True)
            embed.add_field(name=":date: Release Date", value=date or existing_game.get("date", "N/A"), inline=True)
            embed.set_image(url=image_url or existing_game.get("image_url", ""))
            embed.set_footer(text=f"Game {action} by {interaction.user.display_name}")
            embed.timestamp = now
            view = View()
            emoji = self.bot.get_emoji(1144807049297924116)
            button = Button(label="Download", style=discord.ButtonStyle.premium, url=link or existing_game.get("link",""), emoji=emoji)
            view.add_item(button)

            games_channel = self.bot.get_channel(1255987489907277896)
            if games_channel:
                await games_channel.send(embed=embed, view=view)
                await interaction.response.send_message(f"{interaction.user.display_name} {action} a game at <#{games_channel.id}>", ephemeral=False)
            else:
                await interaction.response.send_message("Games channel not found.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

    @app_commands.command(name="listgames", description="List all submitted games")
    async def listgames(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        member = interaction.user
        
        if not any(role.name in self.gaming_role for role in member.roles):
            await interaction.response.send_message(":x: You do not have permission to use this command. You need to be a <@&1256005308740927560>", ephemeral=True)
            return

        games = GameModel.list_game()
        if not games:
            await interaction.followup.send("No games found.", ephemeral=True)
            return

        embed = discord.Embed(title=":clipboard: Game List", color=discord.Color.blue())
        for game in games:
            author = await self.bot.fetch_user(int(game["author_id"]))
            embed.add_field(
                name=game.get("title", "No Title"),
                value=f"Version: {game.get('version', 'N/A')} | Size: {game.get('size', 'N/A')} | Date: {game.get('date', 'N/A')}\nAuthor: {author.display_name}\n[Download]({game.get('link', '#')})",
                inline=False
            )
        await interaction.followup.send(embed=embed, ephemeral=False)
        
    @app_commands.command(name="deletegame", description="Delete a submitted game")
    @app_commands.describe(title="Title of the game to delete",)
    async def deletegame(self, interaction: discord.Interaction, title: str):
        member = interaction.user
        if not any(role.name in self.gaming_role for role in member.roles):
            await interaction.response.send_message(":x: You do not have permission to use this command. You need to be a <@&1256005308740927560>", ephemeral=True)
            return

        game = GameModel.delete_game(title)
        
        if game.deleted_count == 0:
            await interaction.response.send_message(f":x: No game found with the title '{title}'.", ephemeral=False)
            return
        await interaction.response.send_message(f"<a:walter:1260121444269162506> {interaction.user.display_name} successfully deleted {title}", ephemeral=False)
        return
    
    
    @app_commands.command(name="game", description="Retrieve a submitted game")
    @app_commands.describe(title="Title of the game",)
    async def game(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer(thinking=True)
        member = interaction.user
        if not any(role.name in self.gaming_role for role in member.roles):
            await interaction.followup.send(":x: You do not have permission to use this command. You need to be a <@&1256005308740927560>", ephemeral=True)
            return

        game = GameModel.get_game_by_title(title)
        if not game:
            await interaction.followup.send(f":x: No game found with the title '{title}'.", ephemeral=False)
            return
        
        embed = discord.Embed( title=game.get("title"), description=game.get("description", "No description provided."), url=game.get("link"), color=discord.Color.random() )
        
        author = await self.bot.fetch_user(int(game["author_id"]))
        embed.set_thumbnail(url=game.get("image_url"))
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        embed.add_field(name=":tools: Version", value=game.get("version", "N/A"), inline=True)
        embed.add_field(name=":floppy_disk: Size", value=game.get("size", "N/A"), inline=True)
        embed.add_field(name=":date: Release Date", value=game.get("date", "N/A"), inline=True)
        embed.set_image(url=game.get("image_url"))
        embed.set_footer(text=f"Game submitted by {author.display_name}")
        embed.timestamp = game.get("updated_at")
        view = View()
        emoji = self.bot.get_emoji(1144807049297924116)
        button = Button(label="Download", style=discord.ButtonStyle.premium, url=game.get("link", "#"), emoji=emoji)
        view.add_item(button)
        await interaction.followup.send(embed=embed, view=view, ephemeral=False)
        

async def setup(bot):
    await bot.add_cog(AllBotCommands(bot))
