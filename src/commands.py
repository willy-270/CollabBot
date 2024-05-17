from client import bot
import discord
from classes import Part, Collab
import db

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
    same_title = db.title_already_exists(title)

    if same_title:
        await interaction.response.send_message("Collab with that title already exists")
        return
    
    timestamps = timestamps.split(", ")

    parts = []
    part_num = 1
    for timestamp_pair in timestamps:
        part = Part(timestamp_pair, interaction.guild.id, title, part_num)
        parts.append(part)
        part_num += 1

    collab = Collab(title, parts, interaction.user, interaction.channel.id, interaction.guild.id)

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
    collab_part = db.get_part(collab_title, part_num)
    
    if len(collab_part) == 0:
        await interaction.response.send_message("Part not found or is already taken")
        return

    db.take_part(interaction.user.id, collab_title, part_num)

    part_msg = await interaction.channel.fetch_message(collab_part[5])
    part_embed = part_msg.embeds[0]
    part_embed.description = f"Timestamp: {collab_part[1]}\nParticipant: {interaction.user.mention}"
    part_embed.set_thumbnail(url=interaction.user.avatar.url)
    part_embed.color = discord.Color.green()

    await part_msg.edit(embed=part_embed)  
    await interaction.response.send_message("done", ephemeral=True)       