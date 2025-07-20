import discord
from discord.ext import commands
from discord.ui import Button, View
from models.game_model import GameModel
from datetime import datetime, timezone

class AllBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gaming_channel = [1256421833884958800, 903261559181160478, 1255987489907277896, 1395461570972225537]
        self.gaming_role = ["Admin", "Moderator", "Pirata"]

    @commands.command()
    async def game(self, ctx, *, args: str):
        try:
            await ctx.message.delete()

            if ctx.channel.id not in self.gaming_channel:
                await ctx.send("Please use this command at <#1256421833884958800> or <#903261559181160478> or <#1255987489907277896> only.")
                return

            parts = [arg.strip('"') for arg in args.split('"') if arg.strip() and arg != ' ']
            if len(parts) != 7:
                await ctx.send("Please format your command like:\n`!game \"Title\" \"Description\" \"Version\" \"Size\" \"Date\" \"Link\" \"Image URL\"`")
                return

            title, desc, vers, size, date, link, image_url = parts
            now = datetime.now(timezone.utc)

            # Check if game exists
            existing_game = GameModel.get_game_by_title(title)

            if existing_game:
                GameModel.update_game_by_title(title, {
                    "author": str(ctx.author),
                    "author_id": str(ctx.author.id),
                    "description": desc,
                    "version": vers,
                    "size": size,
                    "date": date,
                    "link": link,
                    "image_url": image_url,
                    "updated_at": now
                })
            else:
                GameModel.create_game({
                    "author": str(ctx.author),
                    "author_id": str(ctx.author.id),
                    "title": title,
                    "description": desc,
                    "version": vers,
                    "size": size,
                    "date": date,
                    "link": link,
                    "image_url": image_url,
                    "created_at": now,
                    "updated_at": now
                    }
                )

            # Build embed
            embed = discord.Embed(title=title, description=desc, url=link, color=discord.Color.random())
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar or ctx.author.default_avatar.url)
            embed.add_field(name=":tools: Version", value=vers, inline=True)
            embed.add_field(name=":floppy_disk: Size", value=size, inline=True)
            embed.add_field(name=":date: Release Date", value=date, inline=True)
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Game submitted by {ctx.author.display_name}")
            embed.timestamp = now

            # Build button
            view = View()
            emoji = self.bot.get_emoji(1144807049297924116)
            button = Button(label="Download", style=discord.ButtonStyle.link, url=link, emoji=emoji)
            view.add_item(button)

            games_channel = self.bot.get_channel(1255987489907277896)  # Replace with your actual games channel ID
            if games_channel:
                await games_channel.send(embed=embed, view=view)
                await ctx.send(f"{ctx.author.display_name} posted a game at <#1255987489907277896>")
            else:
                await ctx.send("Games channel not found.")

        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")
                
    @commands.command()
    async def listgames(self, ctx):
        
        if not any(role.name in self.gaming_role for role in ctx.author.roles):
            await ctx.send(f":x: You do not have permission to use this command. You need to be a <@&1256005308740927560>")
            return
        
        games = GameModel.list_game()
        if not games:
            await ctx.send("No games found.")
            return

        embed = discord.Embed(title="📋 Game List", color=discord.Color.blue())
        for game in games:
            embed.add_field(
                name=game.get("title", "No Title"),
                value=f"Version: {game.get('version', 'N/A')} | Size: {game.get('size', 'N/A')} | Date: {game.get('date', 'N/A')}\nAuthor: {game.get('author', 'Unknown')}\n[Download]({game.get('link', '#')})",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AllBotCommands(bot))