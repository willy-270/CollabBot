# CollabBot

A bot to help manage collab lists in discord, made to get rid of the tedious work of manually typing out lists, as well as multiple other benifits


## Commands:

### /make_collab

parameters:

- title
- timestamps
    - Ex: "0:00, 0:30 , 1:00, 1:30" would produce 3 parts, "0:00-0:30", "0:30-1:00", and "1:00-1:30"
- channel
    - The channel to post the collab in
- role_allowed_to_take_parts (optional)
    - Role that is allowed to take parts, if not provided, participants of parts can only be managed by the owner of the collab
- gc_per_part (optional)
    - The amount of grouos and colors given to each part
- yt_link_to_song (optional)
    - if provided, the part messages will include hyperlinks to the song at the part timestamp, it will also be included in the title message

This will then send the list into the specified channel

### /take_part

parameters:

- collab_title
- part_number

Will not work if the part is already taken or if the user is not allowed to take parts due to role settings

### /drop_part

parameters:

- collab_title
- part_number

Will not work if the part is not taken by the user

### /delete_collab

parameters:

- collab_title

Will delete the collab and all of its parts, only usable by the owner of the collab







