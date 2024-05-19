import discord
import db

class Part:
    def __init__(self, 
                 timestamp_pair: str,  
                 guild_id: int, 
                 collab_title: str,
                 part_num: int,
                 msg: discord.Message = None,
                 participant: discord.User = None,
                 prog_status: int = None):
        self.timestamp_pair = timestamp_pair
        self.guild_id = guild_id
        self.collab_title = collab_title
        self.part_num = part_num
        self.participant = participant
        self.msg = msg
        self.prog_status = prog_status

        if not db.part_already_exists(self):
            db.part_init(self)

    def make_part_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = f"**Part {self.part_num}**"
        embed.description = f"**{self.timestamp_pair}**"
        if self.participant != None:
            embed.description += f"\n{self.participant.mention}"
            embed.set_thumbnail(url=self.participant.avatar.url)
            if self.prog_status == 0:
                embed.color = discord.Color.red()
                embed.description += "\n*🚫 No Progress*"
            elif self.prog_status == 1:
                embed.color = discord.Color.yellow()
                embed.description += "\n*🟨 Progress Shown*"
            else:
                embed.color = discord.Color.green()
                embed.description += "\n*✅ Complpeted*"
        else:
            embed.description += "\n*Not taken*"
        
        return embed

    async def take(self, user: discord.User) -> None:
        self.participant = user
        self.prog_status = 0
        part_embed = self.make_part_embed()

        db.update_part_participant(self)

        await self.msg.edit(embed=part_embed) 

    async def drop(self) -> None:
        self.participant = None
        self.prog_status = None
        part_embed = self.make_part_embed()

        db.update_part_participant(self)

        await self.msg.edit(embed=part_embed)

    async def update_part_satus(self, status: int) -> None:
        self.prog_status = status
        part_embed = self.make_part_embed()

        db.update_part_status(self)

        await self.msg.edit(embed=part_embed)

    async def delete_msg(self) -> None:
        await self.msg.delete()

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
        self.timestamp_pairs = timestamp_pairs
        self.title_msg = None

        timestamps = timestamp_pairs.split(", ")

        parts = []
        part_num = 1
        for timestamp_pair in timestamps:
            part = Part(timestamp_pair, guild_id, title, part_num)
            parts.append(part)
            part_num += 1

        self.parts = parts

        if not db.collab_already_exists(self):
            db.collab_init(self)

    def make_collab_title_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = self.title
        embed.description = f"Owner: {self.owner.mention}"

        return embed         

    async def send(self):
        title_embed = self.make_collab_title_embed()
        self.title_msg = await self.channel.send(embed=title_embed)
        db.set_title_msg_id(self)

        for part in self.parts:
            part_embed = part.make_part_embed()

            part.msg = await self.channel.send(embed=part_embed)

            db.set_part_msg_id(part)

    async def delete(self):
        for part in self.parts:
            await part.delete_msg()
        await self.title_msg.delete()
        db.delete_collab(self)



