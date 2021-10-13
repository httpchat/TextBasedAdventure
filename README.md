# Text Based Adventure Jam

_Author: Devin McIntyre_

Our goal is two-fold:

1) Create a text based adventure game engine that can parse a standard file format
2) Create a text based adventure game using the standardized file format

We'll be looking to implement a very, very basic engine that includes support for rooms, items, doors, commands, and effects, as well as an inventory system.

## What you need to build
Provided below is a definition for a text based adventure game configuration.  The configuration contains a list of items, the commands they take, the effects they can have, the rooms that hold them, the doors that connect those rooms, the starting position and the final room.  Your goal is to build an engine that can parse this defintion, and any definition matching the standard, into a playable text based adventure game.

The basics of the game are as follows:

1) Players always start in the room defined by `startingRoomId`.
2) Players have an inventory of infinite size and space, which they can fill with items.
    - Items that are used for a task can be used ONLY ONCE.  After use they should be removed from a players inventory
3) Players can interact with the world by use of text commands.  
    - The expected commands are
        - LOOK
        - TAKE
        - READ
        - USE $A ON $B
        - GO $DIRECTION
        - INVENTORY
    - What these commands should do is outlined below
4) Using commands on items can produce effects
    - Expected effects are
        - UNLOCK_DOOR
        - LOCK_DOOR
        - CHANGE_ITEM_TEXT
    - What these effects should do is outlined below
5) A player's goal is to arrive at the room defined with the `endingRoomId` property


# File Format Breakdown

## Commands:
Commands are the building block of a users interaction with the world.  Users issue commands with or without targets, and are given feedback resulting from the command.  These are verbs, specifying an action, such as "GO", "READ" and "TAKE".

### Command structure
```
{
    "command" : string,
    "text" : string,
    "acceptedItems" : [
        {
            "itemId" : string,
            "text" : string,
            "effectIds" : string[]
        }
    ]
}
```

### Commands to implement:
**LOOK** - displays the text of the LOOK command for the specified object.  Valid objects are any visible objects in a room, and any object in a users inventory.  If no object given, instead display text of the current room, along with any doors and visible items.
- Use
    - Looking at an item : "LOOK book"
    - Looking at a room : "LOOK"

**TAKE** - adds item to inventory if available, hides item when looking at the room.  If no item provided, prompt for an item.  If item provided is invalid, display error message
- Use
    - Specifying no item: "TAKE"
    - Specifying item : "TAKE pizza box"

**READ** - displays the text of the READ command for the specified object.  If no object is given, prompt for an object.  If object is invalid, or object lacks read command, display error message
- Use
    - Specifying object : "READ cheese"

**USE $A ON $B** - Takes two objects and applies any effects if the object $A is allowed to be used on the object $B.  If objects are missing or the combination is invalid, display error message
- Use
    - Specifying objects : "USE book ON book shelf"

**GO $DIRECTION** - Attempts to move the player to the next room in the direction they specify.  If a door exists in the direction, and the door is unlocked, the player is moved to the next room.  If the door exists but is locked, display an error message about the doors status.  If the door doesn't exist, display an error message.
- Use
    - Specifying a direction : "GO north"

**INVENTORY** - Displays any items by name in the users inventory.


## Effects
Effects give us the ability to have latent actions following a users input.  Actions take 0 or more items or doors, specify an effect type, and can provide contextual text to accompany the effect (either by displaying the text to the user, or modifying existing text).  Examples of effects are "UNLOCK_DOOR" and "CHANGE_ITEM_TEXT"

### Effect Structure
```
{
    "id" : string,
    "type" : string,
    "doorIds" : string[],
    "itemIds" : string[],
    "text" : string
}
```

### Effects to implement
**UNLOCK_DOOR** - Unlocks any provided door IDs.  If text is provided, display the text to the user.

**LOCK_DOOR** - Locks any provided door IDs.  If text is provided, display the text to the user.

**CHANGE_ITEM_TEXT** - Updates the descriptive text of an item to the provided text.

## Items
Items provide the user with tools to solve puzzles between rooms.  Items contain lists of valid commands, an ID, a visibility state, and a name.

### Item Structure
```
{
    "id" : string,
    "name" : string,
    "commands" : Command[],
    "visible" : boolean
}
```

## Doors
Doors are used to signify a transition point between rooms. They may be locked or unlocked by effects, a state that is global to the door, and contain an id.

### Door Structure
```
{
    "id" : string,
    "locked" : boolean
}
```

## Rooms
Rooms represent areas of the world.  Each room may have up to 4 doors (One in each cardinal direction), descriptive text, zero or more items, and can be marked as the victory condition.  Reaching the room marked as the victory condition should end the game after printing the descriptive text.

### Room Structure
```
{
    "id" : string,
    "text" : string,
    "itemIds" : string[],
    "doors" : [
        {
            "doorId" : string,
            "direction" : string,
            "connectedRoomId" : string
        }
    ]
}
```

## Full Game Format Structure
```
{
    "items" : Item[],
    "effects" : Effect[],
    "doors" : Door[],
    "rooms" : Room[],
    "startingRoomId" : string,
    "endingRoomId" : string
}
```


# Example of a valid adventure (3 rooms, 2 items, 3 effects, and one simple puzzle):
```json
{
    "items" : [
        {
            "id" : "1",
            "name" : "Book",
            "commands" : [
                {
                    "command" : "LOOK",
                    "text" : "An old book, worn with time."
                },
                {
                    "command" : "TAKE"
                },
                {
                    "command" : "READ",
                    "text" : "The old book is filled with mostly useless, outdated information"
                }
            ],
            "visible" : true
        },
        {
            "id" : "2",
            "name" : "Book Shelf",
            "commands" : [
                {
                    "command" : "LOOK",
                    "text" : "An old dusty bookshelf full of tomes.  One seems to be missing."
                },
                {
                    "command" : "USE",
                    "acceptedItem" : [
                        {
                            "itemId" : "1",
                            "text" : "You place the book into it's place on the shelf",
                            "effectIds" : ["1", "2", "3"]
                        }
                    ]
                }
            ],
            "visible" : true
        }
    ],
    "effects" : [
        {
            "id" : "1",
            "type": "UNLOCK_DOOR",
            "doorIds" : ["2"],
            "text": "The door to the east makes a satisfying click."
        },
        {
            "id" : "2",
            "type": "LOCK_DOOR",
            "doorIds" : ["1"],
            "text": "The door to the south makes a unsatisfying click."
        },
        {
            "id" : "3",
            "type" : "CHANGE_ITEM_TEXT",
            "itemIds" : ["2"],
            "text" :"An old dusty bookshelf full of tomes."
        }
    ],
    "doors" : [
        {
            "id" : "1",
            "locked" : false 
        },
        {
            "id" : "2",
            "locked" : true
        }
    ], 
    "rooms" : [
        {
            "id": "1",
            "text" : "A simple room with a bed and a side table.",
            "itemIds" : ["1"],
            "doors" : [
                {
                    "doorId" : "1",
                    "direction" : "NORTH",
                    "connectedRoomId" : "2"
                }
            ]
        },
        {
            "id" : "2",
            "text" : "A simple room with some furniture.",
            "itemIds" : ["2"],
            "doors" : [
                {
                    "doorId" : "2",
                    "direction" : "EAST",
                    "connectedRoomId" : "3"
                },
                {
                    "doorId" : "1",
                    "direction" : "SOUTH",
                    "connectedRoomId" : "1"
                }
            ]
        },
        {
            "id" : "3",
            "text" : "The world outside is bright, you have escaped the dungeon!"
        }
    ],
    "startingRoomId" : "1",
    "endingRoomId" : "3"
}
```