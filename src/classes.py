import discord
import db

class Part:
    def __init__(self, 
                 timestamp_pair: str,  
                 guild_id: int, 
                 collab_title: str,
                 part_num: int,
                 msg: discord.Message = None,
                 participant: discord.User = None):
        self.timestamp_pair = timestamp_pair
        self.guild_id = guild_id
        self.collab_title = collab_title
        self.part_num = part_num
        self.participant = participant
        self.msg = msg

        db.part_init(timestamp_pair, guild_id, collab_title, part_num, None, None)

    def make_part_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = f"Part {self.part_num}"
        embed.description = f"Timestamp: {self.timestamp_pair}"
        if self.participant != None:
            embed.description += f"\nParticipant: {self.participant.mention}"
            embed.set_thumbnail(url=self.participant.avatar.url)
            embed.color = discord.Color.green()
        else:
            embed.description += "\nParticipant: None"
        
        return embed

    async def take(self, user: discord.User) -> None:
        self.participant = user
        part_embed = self.make_part_embed()

        db.take_part(self.participant.id, self.collab_title, self.part_num)

        await self.msg.edit(embed=part_embed) 

    async def drop(self) -> None:
        self.participant = None
        part_embed = self.make_part_embed()

        db.drop_part(self.collab_title, self.part_num)

        await self.msg.edit(embed=part_embed)

class Collab:
    def __init__(self, 
                 title: str, 
                 owner: discord.Member, 
                 channel: discord.TextChannel, 
                 guild_id: int,
                 timestamp_pairs: str):
        self.title = title
        self.owner = owner
        self.channel = channel
        self.guild_id = guild_id

        timestamps = timestamp_pairs.split(", ")

        parts = []
        part_num = 1
        for timestamp_pair in timestamps:
            part = Part(timestamp_pair, guild_id, title, part_num)
            parts.append(part)
            part_num += 1

        self.parts = parts

        db.collab_init(title, owner.id, channel.id, guild_id)

    def make_collab_title_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = self.title
        embed.description = f"Owner: {self.owner.mention}"

        return embed         

    async def send(self):
        title_embed = self.make_collab_title_embed()
        await self.channel.send(embed=title_embed)

        for part in self.parts:
            part_embed = part.make_part_embed()

            part_msg = await self.channel.send(embed=part_embed)
            part.msg_id = part_msg.id

            db.set_msg_id(part_msg.id, self.title, part.part_num)



