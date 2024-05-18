import sqlite3
from client import bot
import discord
from classes import Part

conn = sqlite3.connect('collab.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Parts (
            id INTEGER PRIMARY KEY,
            timestamp_pair TEXT, 
            guild_id INTEGER, 
            collab_title TEXT, 
            part_num INTEGER, 
            msg_id INTEGER, 
            participant_id INTEGER
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Collabs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            owner_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER
        )''')

    conn.commit()

def part_init(timestamp_pair: str, guild_id: int, collab_title: str, part_num: int, msg: discord.Message, participant: discord.User):
    if msg:
        msg_id = msg.id
    else:
        msg_id = None

    if participant:
        participant_id = participant.id
    else:
        participant_id = None

    cursor.execute('''
            INSERT INTO Parts (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id))
    conn.commit()

def collab_init(title: str, owner_id: int, channel_id: int, guild_id: int):
    cursor.execute('''
            INSERT INTO Collabs (title, owner_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)''',
            (title, owner_id, channel_id, guild_id))       
    conn.commit() 

def set_msg_id(msg_id: int, collab_title: str, part_num: int, guild_id: int):
    cursor.execute('''
        UPDATE Parts
        SET msg_id = ?
        WHERE collab_title = ?
        AND part_num = ?
        AND guild_id = ?''',
        (msg_id, collab_title, part_num, guild_id))
    conn.commit()

def title_already_exists(title: str, guild_id: int) -> bool:
    return bool(cursor.execute('''SELECT * FROM Collabs 
                               WHERE title = ?
                               AND guild_id = ?''', 
                               (title, guild_id,)).fetchone())
    
async def get_part_in_server(collab_title: str, part_num: int, guild_id: int) -> Part | None:
    part_r = cursor.execute('''
        SELECT * FROM Parts
        WHERE collab_title = ?
        AND part_num = ?
        AND guild_id = ?''',
        (collab_title, part_num, guild_id)).fetchone()
    
    channel_id_r = cursor.execute('''
        SELECT * from Collabs
        WHERE title = ?
        AND guild_id = ?''',
        (collab_title, guild_id)).fetchone()
    
    if channel_id_r:
        channel_id = channel_id_r[3]
    else:
        return None

    if part_r:
        if part_r[6] == None:
            participant = None
        else:
            participant = await bot.fetch_user(part_r[6])
        channel = bot.get_channel(channel_id)
        message = await channel.fetch_message(part_r[5])
        return Part(part_r[1], part_r[2], part_r[3], part_r[4], message, participant)
    else:
        return None
    
def update_part_participant(participant_id: int | None, collab_title: str, part_num: int, guild_id) -> None:
    cursor.execute('''UPDATE Parts
                      SET participant_id = ?
                      WHERE collab_title = ?
                      AND part_num = ?
                      AND guild_id = ?''',
                      (participant_id, collab_title, part_num, guild_id))
    conn.commit()

def get_collab_titles(guild_id: int) -> list[str]:
    return [title[0] for title in cursor.execute('''
        SELECT title FROM Collabs
        WHERE guild_id = ?''',
        (guild_id,)).fetchall()]

def part_already_exists(collab_title: str, part_num: int, guild_id: int) -> bool:
    return bool(cursor.execute('''SELECT * FROM Parts
                               WHERE collab_title = ?
                               AND part_num = ?
                               AND guild_id = ?''', 
                               (collab_title, part_num, guild_id,)).fetchone())

def get_collab_owner_id(collab_title: str, guild_id: int) -> int | None:
    r = cursor.execute('''SELECT owner_id FROM Collabs
                          WHERE title = ?
                          AND guild_id = ?''',
                          (collab_title, guild_id)).fetchone()
    if r:
        return r[0]
    else:
        return None

def delete_collab(collab_title: str, guild_id: int) -> None:
    cursor.execute('''DELETE FROM Collabs
                      WHERE title = ?
                      AND guild_id = ?''',
                      (collab_title, guild_id))
    cursor.execute('''DELETE FROM Parts
                      WHERE collab_title = ?
                      AND guild_id = ?''',
                      (collab_title, guild_id))
    conn.commit()
    
