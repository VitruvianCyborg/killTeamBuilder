class Model:
    def __init__(self, id, name, cost, chars, rules, sharedRules, links):
        self.name = name
        self.id = id
        self.cost = cost
        self.chars = chars
        self.rules = rules
        self.sharedRules = sharedRules
        self.links = links

class Rule:
    def __init__(self, id, name, text, ruleType):
        self.id = id
        self.name = name
        self.text = text
        self.ruleType = ruleType

class Armoury:
    def __init__(self, id, name, cost, chars, type):
        self.id = id
        self.name = name
        self.cost = cost
        self.chars = chars
        self.type = type

class Collections:
    def __init__(self, id, name, contents):
        self.id = id
        self.name = name
        self.contents = contents

#takes tree element and outputs list of Rule classes
def ParseRules(root):
    rules = []
    #loops through tree for all elements that match the selection no matter where they are
    for node in root.iterfind('.//rule'):
        #id, name type taken directly from node attributes (root>rules>rule)
        id = node.get('id')
        name = node.get('name')
        #searches for desciption in (root>rules>rule) and appends with .text to pull through contents of element
        text = node.find('description').text
        ruleType = 'rule'
        #new class instantiated with results of this iteration of for loop
        newRule = Rule(id, name, text, ruleType)
        #class added list as next item
        rules.append(newRule)
    #also looping through tree to find shared rules
    for node in root.iterfind('.sharedProfiles//profile'):
        id = node.get('id')
        name = node.get('name')
    #searches for rule desciptions from (root>shareprofiles>profile>characteristics>characteristic)
        text = node.find('./characteristics/characteristic').text
        ruleType = 'ability'
        newRule = Rule(id, name, text, ruleType)
        rules.append(newRule)
    return rules

#takes tree element and outputs list of Model classes and list of Armoury classes
def ParseSelectionEntry(root):
    models = []
    armoury = []
    for node in root.iterfind('./sharedSelectionEntries/selectionEntry'):
        #loop selectionEntry for type= model only
        if node.get('type') == 'model':
            id = node.get('id')
            name = node.get('name')
            cost = node.find('./costs/cost').get('value')
            chars = {}
            rules = {}
            sharedRules = []
            links = []
            for elem in node.iterfind('./profiles/profile'):
                #checks if model has any special rules and generates dict
                if elem.get('typeName') == 'Ability':
                    ruleName = elem.get('name')
                    ruleText = elem.find('./characteristics/characteristic').text
                    rules[ruleName] = ruleText
                elif elem.get('typeName') == 'Model':
                    for char in elem.findall('./characteristics/characteristic'):
                        charName = char.get('name')
                        charText = char.text
                        #creates dict containing models characteristics (eg. WS BS W T I A)
                        chars[charName] = charText
                else:
                    continue
            #loops through infoLinks to find targetIds of collections that should be included in models entry
            #ie Global faction rules, shared rules
            for elem in node.iterfind('./infoLinks/infoLink'):
                sharedRulesId = elem.get('targetId')
                sharedRules.append(sharedRulesId)
            #loops through entryLinks to find targetIds of collections that should be in model entry
            #ie Wargear, subfactio bonus
            for elem in node.iterfind('./entryLinks/entryLink'):
                links.append(elem.get('targetId'))
            #class created with id, name, cost (int), chars (dict), rules(dict if present, last element so easily omitted)
            newModel = Model(id, name, cost, chars, rules, sharedRules, links)
            models.append(newModel)
        #loop selectionEntry for type=upgrade which is equivalent to purchasable equipment
        elif node.get('type') == 'upgrade':
            id = node.get('id')
            name = node.get('name')
            cost = node.find('./costs/cost').get('value')
            chars = []
            #returns Weapon or Wargear
            type = node.find('./profiles/profile').get('typeName')
            #gives weapon stats and any special rules
            #rules are 'Abilities' if weapon and 'Ability' if wargear
            #loops to find multiple entries
            for elem in node.iterfind('./profiles/profile'):
                profName = elem.get('name')
                #Stores in dict with Name as 1st entry
                profChars = {}
                profChars['Name'] = profName
                for prof in elem.findall('./characteristics/characteristic'):
                    charName = prof.get('name')
                    charText = prof.text
                    profChars[charName] = charText
                chars.append(profChars)
            newArmoury = Armoury(id, name, cost, chars, type)
            armoury.append(newArmoury)
        else:
            continue
    return models, armoury

#loops for sharedSelectionEntryGroups to get collections of rules, wargear etc which models will reference
def ParseCollections(root):
    collections = []
    for node in root.iterfind('./sharedSelectionEntryGroups/selectionEntryGroup'):
        id = node.get('id')
        name = node.get('name')
        contents = []
        for elem in node.iterfind('./entryLinks/entryLink'):
            targetId = elem.get('targetId')
            contents.append(targetId)
        if not contents:
            continue
        else:
            newCollection = Collections(id, name, contents)
            collections.append(newCollection)
    for node in root.iterfind('./sharedSelectionEntryGroups/selectionEntryGroup'):
        id = node.get('id')
        name = node.get('name')
        contents = []
        for elem in node.iterfind('./selectionEntries/selectionEntry/categoryLinks/categoryLink'):
            targetId = elem.get('targetId')
            contents.append(targetId)
        if not contents:
            continue
        else:
            newCollection = Collections(id, name, contents)
            collections.append(newCollection)
    return collections