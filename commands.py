from client import bot
import discord
from classes import Part, Collab, Guild

guilds = []

@bot.tree.command(
    name="make_collab",
    description="Create a new collab"
)
@discord.app_commands.describe(
    timestamps="seperate by comma & space, ex: 0:00-0:10, 0:10-0:20, and so on",
)
async def make_collab(
    interaction: discord.Interaction,
    title: str,
    timestamps: str,
):
    timestamps = timestamps.split(", ")

    parts = []
    for timestamp_pair in timestamps:
        part = Part(timestamp_pair, None, None)
        parts.append(part)

    collab = Collab(title, parts, interaction.user, channel_id=interaction.channel.id)

    if guilds == []:
        guild = Guild(interaction.guild.id, [collab])
        guilds.append(guild)
    else:
        for guild in guilds:
            if guild.guild_id == interaction.guild.id:
                guild.add_collab(collab)
                break
            else:
                guild = Guild(interaction.guild.id, [collab])
                guilds.append(guild)

    await collab.send(interaction.channel)
    await interaction.response.send_message("done", ephemeral=True)

    
@bot.tree.command(
    name="take_part",
    description="Join a collab"
)
async def take_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int,
):
    current_guild = None

    for guild in guilds:
        if guild.guild_id == interaction.guild.id:
            current_guild = guild
            break
        else:
            return await interaction.response.send_message("No collabs in this server")
        
    for collab in current_guild.collabs:
        if collab.title == collab_title:
            if part_num > len(collab.parts) or part_num < 1:
                return await interaction.response.send_message("Invalid part number")
            elif collab.parts[part_num - 1].participant:
                return await interaction.response.send_message("Part already taken")
            else:
                await collab.take_part(part_num, interaction.user)
                return await interaction.response.send_message("Part taken")     
        else:
            return await interaction.response.send_message("Collab not found")