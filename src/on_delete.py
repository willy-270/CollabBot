from client import bot
import discord
import db

@bot.event
async def on_message_delete(message: discord.Message):
    if not message.author.bot:
        return

    collab = await db.get_collab_from_msg_id(message.id)

    if not collab:
        return
    
    deleted = False

    if collab.title_msg == None:
        deleted = True

    for part in collab.parts:
        if part.msg == None:
            if deleted == True:
                return
            deleted = True

    await message.channel.send("Resending list due to deletion. If you want to delete this, us the /delete_collab command")

    await collab.delete(False)
    await collab.send()