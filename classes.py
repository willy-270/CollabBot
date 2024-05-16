import discord
from client import bot

class Part:
    def __init__(self, timestamp_pair: str, msg_id: int, participant: discord.Member):
        self.timestamp_pair = timestamp_pair
        self.msg_id = msg_id
        self.participant = participant

class Collab:
    def __init__(self, title: str, parts: list[Part], owner: discord.Member, channel_id: int):
        self.title = title
        self.parts = parts
        self.owner = owner
        self.channel_id = channel_id

    async def send(self, channel: discord.TextChannel):
        title_embed = discord.Embed()
        title_embed.title = self.title
        title_embed.description = f"Owner: {self.owner.mention}"
        await channel.send(embed=title_embed)

        part_num = 1
        for part in self.parts:
            part_embed = discord.Embed()
            part_embed.title = f"Part {part_num}"
            part_embed.description = f"Timestamp: {part.timestamp_pair}"
            if part.participant != None:
                part_embed.description += f"\nParticipant: {part.participant.mention}"
                part_embed.thumbnail = part.participant.avatar_url
                part_embed.color = discord.Color.green()
            else:
                part_embed.description += "\nParticipant: None"
                

            part_msg = await channel.send(embed=part_embed)
            part.msg_id = part_msg.id
            part_num += 1

    async def take_part(self, part_num: int, participant: discord.Member):
        channel = bot.get_channel(self.channel_id)
        part = self.parts[part_num - 1]
        part_msg = await channel.fetch_message(part.msg_id)

        part_embed = part_msg.embeds[0]
        part_embed.description = f"Timestamp: {part.timestamp_pair}\nParticipant: {participant.mention}"
        part_embed.set_thumbnail(url=participant.avatar.url)
        part_embed.color = discord.Color.green()

        await part_msg.edit(embed=part_embed)

class Guild:
    def __init__(self, guild_id: int, collabs: list[Collab]):
        self.guild_id = guild_id
        self.collabs = collabs

    def add_collab(self, collab: Collab):
        self.collabs.append(collab)