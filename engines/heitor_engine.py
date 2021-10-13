# Author: Heitor Chang

import json


def convertListOfObjects(rawList):
    convertedDict = {}
    for obj in rawList:
        if 'id' in obj:
            convertedDict[obj['id']] = obj
        elif 'command' in obj:
            convertedDict[obj['command']] = obj
        elif 'doorId' in obj:
            convertedDict[obj['doorId']] = obj
    return convertedDict


def convertWorldToKeys(rawWorld):
    """Add objects with ID attributes to a dict, where the value is
    the object itself, associated to the ID as key.
    (Avoid linear searches to retrieve an item.)"""
    
    world = {}

    # iterate over top-level keys
    for k in rawWorld:
        if isinstance(rawWorld[k], str):
            world[k] = rawWorld[k]
        else:
            world[k] = convertListOfObjects(rawWorld[k])
            if k == 'items':
                for item in world['items'].values():
                    item['commands'] = convertListOfObjects(item['commands'])
            elif k == 'rooms':
                for room in world['rooms'].values():
                    if 'doors' in room:
                        room['doors'] = convertListOfObjects(room['doors'])
    return world


class Player:
    def __init__(self, world):
        self.inventory = []


class Game:
    def __init__(self, jsonFilename):
        with open(jsonFilename, encoding="utf-8") as json_in:
            self.rawWorld = json.load(json_in)
        self.world = convertWorldToKeys(self.rawWorld)
        self.player = Player(self.world)

        # store a reference to the entire room where the player is
        self.playerRoom = self.world['rooms'][self.world['startingRoomId']]


    def showState(self):
        print(json.dumps(self.world, indent=2, sort_keys=True))


    def showTopLevel(self, key):
        print(json.dumps(self.world[key], indent=2, sort_keys=True))
        
        
    def act(self, textCommand):
        """Dispatch to the appropriate method."""
        tokens = textCommand.split()
        tokens[0] = tokens[0].upper()  # allow lowercase input
        
        if tokens[0] == "LOOK":
            self.look(textCommand)
        elif tokens[0] == "READ":
            self.read(textCommand)
        elif tokens[0] == "INVENTORY":
            print("You have:")
            if len(self.player.inventory) == 0:
                print("Nothing.")
            else:
                print("\n".join(self.world['items'][itemId]['name'] for itemId in self.player.inventory))
        elif tokens[0] == "GO":
            goState = self.go(tokens[1])
            if goState == "WIN":
                return "WIN"
        elif tokens[0] == "TAKE":
            self.take(" ".join(tokens[1:]))
        elif tokens[0] == "USE":
            body = " ".join(tokens[1:]).lower()
            obj, target = body.split(" on ")
            self.use(obj, target)
        else:
            print("act ERROR: unknown action.")
                
    
    def lookAtItem(self, itemName, alternativeAction=None):
        """Return the text describing the item. Apply READ if optional parameter is given"""
        action = "LOOK"
        if alternativeAction is not None:
            action = alternativeAction
        for item in self.world['items'].values():
            if item['name'].lower() == itemName.lower():                
                print(item['commands'][action]['text'])
                break
        else:
            print("lookAtItem: Item not found.")


    def describeItemById(self, itemId):
        print(f"There is an item: '{self.world['items'][itemId]['name']}'.", end=" ")
        print(self.world['items'][itemId]['commands']['LOOK']['text'])
                        
                
    def look(self, textCommand):
        tokens = textCommand.split()
        if len(tokens) == 1:
            room = self.playerRoom
            print("Your surroundings are:", room['text'])

            # print items in room
            if 'itemIds' in room:
                for itemId in room['itemIds']:
                    self.describeItemById(itemId)
                
            # check for doors
            if 'doors' in room:
                print()
                for door in room['doors'].values():
                    print("There is a door going", door['direction'])
        elif len(tokens) > 1:
            item = " ".join(tokens[1:])
            self.lookAtItem(item)


    def read(self, textCommand):
        tokens = textCommand.split()
        if len(tokens) > 1:
            item = " ".join(tokens[1:])
            self.lookAtItem(item, "READ")  # apply READ instead of LOOK
        else:
            "read: An object must be given."
            
            
    def tryDoor(self, direction):
        """Check if the door is unlocked and return the connectedRoomId"""
        for door in self.playerRoom['doors'].values():
            if door['direction'].lower() == direction.lower():
                if not self.world['doors'][door['doorId']]['locked']:
                    return door['doorId']
                else:
                    print("tryDoor: door is locked.")
                    return False
        print(f"tryDoor: no door going {direction}.")
        return False
                
                
    def go(self, direction):
        if doorId := self.tryDoor(direction):
            self.playerRoom = self.world['rooms'][self.playerRoom['doors'][doorId]['connectedRoomId']]
            print(f"You have moved {direction}.")
            if self.playerRoom['id'] == self.world['endingRoomId']:
                self.look("LOOK")
                print("A WINNER IS YOU!!!!!11")
                return "WIN"


    def getItemId(self, itemName):
        for item in self.world['items'].values():
            if item['name'].lower() == itemName.lower():
                return item['id']
        print(f"getItemId ERROR: {itemName} not found.")
        
    
    def take(self, itemName):
        room = self.playerRoom
        roomItems = room['itemIds']
        itemId = self.getItemId(itemName)
        if itemId in roomItems:
            self.player.inventory.append(itemId)
            roomItems.remove(itemId)
            print(f"{itemName} is in hand.")
        else:
            print("take ERROR: item not found.")


    def use(self, objName, targetName):
        objId = self.getItemId(objName)
        targetId = self.getItemId(targetName)
        if objId in self.player.inventory:
            if targetId in self.playerRoom['itemIds']:
                if "USE" in self.world['items'][targetId]['commands']:
                    print(f"Using {objName} on {targetName}")
                    for item in self.world['items'][targetId]['commands']['USE']['acceptedItem']:
                        if item['itemId'] == objId:
                            # apply effects
                            print(item['text'])
                            self.applyEffects(item['effectIds'])
                    self.player.inventory.remove(objId)
                else:
                    print(f"use ERROR: {targetName} cannot be targeted.")
                    return
            else:
                print(f"use ERROR: {targetName} not present in the room.")
        else:
            print(f"use ERROR: {objName} is not in your inventory.")


    def alterDoor(self, doorId, alterType):
        lockStatus = False if alterType == 'UNLOCK_DOOR' else True
        self.world['doors'][doorId]['locked'] = lockStatus
        
    
    def applyEffects(self, effectIds):
        for effect in self.world['effects'].values():
            if effect['id'] in effectIds:
                print(effect['text'])
                effectType = effect['type']
                if 'LOCK_DOOR' in effectType:
                    for doorId in effect['doorIds']:
                        self.alterDoor(doorId, effectType)
                elif 'CHANGE_ITEM_TEXT' == effectType:
                    if 'itemIds' in effect:
                        for itemId in effect['itemIds']:
                            self.world['items'][itemId]['commands']['LOOK']['text'] = effect['text']
        

def playGame(world="sample_world.json"):
    game = Game(world)
    print("Welcome to HTTPS Adventure, enjoy the game! Type 'q' and Enter to quit.")
    print()
    while True:
        action = input("? ")
        if action.lower() == 'q':
            print("Goodbye.")
            break
        gameState = game.act(action)
        if gameState == "WIN":
            break


    
