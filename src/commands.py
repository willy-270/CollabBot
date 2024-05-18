from client import bot
import discord
import db
from classes import Collab

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
    channel: discord.TextChannel
):
    title = title.lower()
    same_title = db.title_already_exists(title, interaction.guild.id)

    if same_title:
        await interaction.response.send_message("Collab with that title already exists in this server")
        return

    collab = Collab(title, interaction.user, channel, interaction.guild.id, timestamps)
    await collab.send()

    await interaction.response.send_message("done", ephemeral=True)

@bot.tree.command(
    name="take_part",
    description="Join a collab"
)
async def take_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int
):
    part = await db.get_part_from_server(collab_title, part_num, interaction.guild.id)
    
    if not part:
        await interaction.response.send_message("Part not found in this server")
        return
    
    if part.participant != None:
        await interaction.response.send_message("Part already taken")
        return

    await part.take(interaction.user)
    await interaction.response.send_message("done")

@bot.tree.command(
    name="drop_part",
    description="Leave a collab"
)
async def drop_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int,
):
    part = await db.get_part_from_server(collab_title, part_num, interaction.guild.id)
    
    if not part:
        await interaction.response.send_message("Part not found in this server")
        return

    if part.participant != interaction.user:
        await interaction.response.send_message("Part is either taken by someone else or is already empty")
        return

    await part.drop()
    await interaction.response.send_message("done")

@bot.tree.command(
    name="delete_collab",
    description="Delete a collab"
)
async def delete_collab(
    interaction: discord.Interaction,
    collab_title: str
):
    collab = await db.get_collab_from_server(collab_title, interaction.guild.id)

    if not collab:
        await interaction.response.send_message("Collab not found in this server")
        return
    
    if collab.owner != interaction.user:
        await interaction.response.send_message("You are not the owner of this collab")
        return
    
    await collab.delete()
    await interaction.response.send_message("done")

def collab_title_autocomplete(command_func):
    '''
    takes in a command function, funcion must have collab_title: str as a parameter
    returns an autocomplete function for that command function
    '''
    @command_func.autocomplete("collab_title")
    async def autocomplete(
        interaction: discord.Interaction,
        current: str
    ) -> list[discord.app_commands.Choice]:
        collab_titles = db.get_collab_titles(interaction.guild.id)

        return [discord.app_commands.Choice(name=title, value=title) for title in collab_titles if current.lower() in title.lower()]
    return autocomplete

collab_title_autocomplete(take_part)
collab_title_autocomplete(drop_part)
collab_title_autocomplete(delete_collab)
    