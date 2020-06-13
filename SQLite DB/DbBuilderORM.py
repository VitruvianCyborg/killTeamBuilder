# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 17:47:01 2019

@author: Vitruvian
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#importing element tree to load xml file
import xml.etree.ElementTree as ET
#importing custom files to parse and build db
import ParseXML as PARSE

#class constructor used by sqlalchemy to build tables using metadata
Base = declarative_base()

#link table between models and rules
class ModelSharedRules(Base):
    __tablename__ = 'model_shared_rules'
    model_id = Column(String(19), ForeignKey('model_table.model_id'), primary_key=True)
    shared_rules_id = Column(String(19), ForeignKey('shared_rules.shared_rules_id'), primary_key=True)

#link table between rule collections and model
class ModelLinks(Base):
    __tablename__ = 'model_links'
    model_id = Column(String(19), ForeignKey('model_table.model_id'), primary_key=True)
    collection_id = Column(String(19), ForeignKey('collection_table.collection_id'), primary_key=True)

#table for model stats
class ModelTable(Base):
    __tablename__ = 'model_table'
    model_id = Column(String(19), primary_key=True)
    model_name = Column(String(200), nullable=False)
    model_cost = Column(Integer, nullable=False)
    chars = relationship('ModelChars', backref=backref('model_chars', uselist=False))
    model_rules = relationship('ModelRules', backref='model_table')
    shared_rules = relationship('SharedRules', secondary='model_shared_rules')
    model_links = relationship('CollectionTable', secondary='model_links')

#table only for core char numbers, 1-1 with model table
class ModelChars(Base):
    __tablename__ = 'model_chars'
    char_m = Column(String(5), nullable=False)
    char_ws = Column(String(5), nullable=False)
    char_bs = Column(String(5), nullable=False)
    char_s = Column(Integer, nullable=False)
    char_t = Column(Integer, nullable=False)
    char_w = Column(Integer, nullable=False)
    char_a = Column(Integer, nullable=False)
    char_ld = Column(Integer, nullable=False)
    char_sv = Column(String(5), nullable=False)
    char_max = Column(Integer, nullable=False)
    model_id = Column(String(19), ForeignKey('model_table.model_id'), primary_key=True)

#all rules that are individual to the one model entry, many-one with model table
class ModelRules(Base):
    __tablename__ = 'model_rules'
    model_rule_name = Column(String(50), primary_key=True)
    model_rule_text = Column(String, nullable=False)
    model_id = Column(String(19), ForeignKey('model_table.model_id'), nullable=False)

#all equipment including weapons and wargear
class ArmouryTable(Base):
    __tablename__ = 'armoury'
    armoury_id = Column(String(19), primary_key=True)
    armoury_name = Column(String(50), nullable=False)
    armoury_cost = Column(Integer, nullable=False)
    armoury_type = Column(String(50), nullable=False)
    profile_id = relationship("ArmouryProfiles", backref='armoury')
#    collection_id = relationship('CollectionTable', backref='armoury')

#profiles of individual equipment to account for multiple profile weapons, many-one with armoury table
class ArmouryProfiles(Base):
    __tablename__ = 'armoury_profiles'
    profile_name = Column(String(50), primary_key=True)
    profile_ability = Column(String, nullable=False)
    profile_rng = Column(String(5))
    profile_s = Column(Integer)
    profile_d = Column(Integer)
    profile_ap = Column(String(5))
    profile_type = Column(String(50))
    armoury_id = Column(String(19), ForeignKey('armoury.armoury_id'), nullable=False)

#all rules which apply to more than one model entry
class SharedRules(Base):
    __tablename__ = 'shared_rules'
    shared_rules_id = Column(String(19), primary_key=True)
    shared_rules_name = Column(String(100), nullable=False)
    shared_rules_text = Column(String, nullable=False)
#    collection_id = relationship('CollectionTable', backref='shared_rules')
    model_id = relationship('ModelTable', secondary='model_shared_rules')

#xml contains collections which are groups of equipment or rules, collection table generates collection id for each member
#of a collection so model links can retrieve
class CollectionTable(Base):
    __tablename__ = 'collection_table'
    collection_table_id = Column(Integer, primary_key=True)
    collection_id = Column(String(19), nullable=False)
    collection_name = Column(String(50), nullable=False)
    shared_rules_id = Column(String(19), ForeignKey('shared_rules.shared_rules_id'))
    armoury_id = Column(String(19), ForeignKey('armoury.armoury_id'))
    model_id = relationship('ModelTable', secondary='model_links')

#all functions below create list of table classes from output of ParseXML.py
#creates instances of relevant table classes
#explicit declaration required as not overriding constructor of declarative_base()
def CreateModelTable(modelList):

    def CreateModelChars(modelId, charDict):
        newCharRow = ModelChars(
                char_m = charDict["M"],
                char_ws = charDict["WS"],
                char_bs = charDict["BS"],
                char_s = charDict["S"],
                char_t = charDict["T"],
                char_a = charDict["A"],
                char_w = charDict["W"],
                char_ld = charDict["Ld"],
                char_sv = charDict["Sv"],
                char_max = charDict["Max"],
                model_id = modelId
                )
        return newCharRow

    #returns list of rule classes to account for multiple unique rules
    def CreateModelRules(modelId, ruleDict):
        modelRules = []
        for ruleName, ruleText in ruleDict.items():
            newRuleRow = ModelRules(
                    model_rule_name = ruleName,
                    model_rule_text = ruleText,
                    model_id = modelId
                    )
            modelRules.append(newRuleRow)
        return modelRules

    def CreateModelSharedRules(modelId, sharedRulesList):
        modelSharedRules = []
        for ruleID in sharedRulesList:
            newSharedRule = ModelSharedRules(
                    model_id = modelId,
                    shared_rules_id = ruleID
                    )
            modelSharedRules.append(newSharedRule)
        return modelSharedRules

    def CreateModelLinks(modelId, linkList):
        modelLinks = []
        for collectionID in linkList:
            newLink = ModelLinks(
                    model_id = modelId,
                    collection_id = collectionID
                    )
            modelLinks.append(newLink)
        return modelLinks

    models = []
    for model in modelList:
        id = model.id
        currentModelBase = ModelTable(
            model_id = id,
            model_name = model.name,
            model_cost = model.cost
            )
        currentModelChars = CreateModelChars(id, model.chars)
        currentModelRules = CreateModelRules(id, model.rules)
        currentModelSharedRules = CreateModelSharedRules(id, model.sharedRules)
        currentModelLinks = CreateModelLinks(id, model.links)
        currentModel = (
                currentModelBase,
                currentModelChars,
                currentModelRules,
                currentModelSharedRules,
                currentModelLinks
                )
        #list of tuples containing all info from one model
        models.append(currentModel)
    return models

def CreateRuleTable(ruleList):
    rules = []
    for rule in ruleList:
        newRuleRow = SharedRules(
            shared_rules_id = rule.id,
            shared_rules_name = rule.name,
            shared_rules_text = rule.text
            )
        rules.append(newRuleRow)
    return rules

def CreateArmouryTable(armouryList):

    def CreateArmouryProfiles(armouryId, armouryType, profileList):
        profiles = []
        for profile in profileList:
            #checks for weapon or wargear to simplify declarations
            if armouryType == "Wargear":
                wargearProfile = ArmouryProfiles(
                        profile_name = profile["Name"],
                        profile_ability = profile["Ability"],
                        armoury_id = armouryId
                        )
                profiles.append(wargearProfile)
            elif armouryType == "Weapon":
                weaponProfile = ArmouryProfiles(
                        profile_name = profile["Name"],
                        profile_ability = profile["Abilities"],
                        profile_rng = profile["Range"],
                        profile_s = profile["S"],
                        profile_d = profile["D"],
                        profile_ap = profile["AP"],
                        profile_type = profile["Type"],
                        armoury_id = armouryId
                        )
                profiles.append(weaponProfile)
        return profiles

    armoury = []
    for armouryItem in armouryList:
        id = armouryItem.id
        type = armouryItem.type
        currentArmouryProfiles = CreateArmouryProfiles(id, type, armouryItem.chars)
        currentArmouryItem = ArmouryTable(
                armoury_id = id,
                armoury_name = armouryItem.name,
                armoury_cost = armouryItem.cost,
                armoury_type = type
                )
        currentArmoury = (currentArmouryItem,currentArmouryProfiles)
        armoury.append(currentArmoury)
    return armoury

def CreateCollectionTable(collectionList,armouryList):
    collections, armouryIdList = [], []
    #build list of IDs in armoury to allow type checking
    for armoury in armouryList:
        armouryIdList.append(armoury.id)
    for collection in collectionList:
        id = collection.id
        name = collection.name
        #loop for id of item in the collection
        for contentID in collection.contents:
            #implement check to determine if id is an armoury item or not
            if contentID in armouryIdList:
                currentCollection = CollectionTable(
                        collection_id = id,
                        collection_name = name,
                        armoury_id = contentID
                        )
                collections.append(currentCollection)
            else:
                currentCollection = CollectionTable(
                        collection_id = id,
                        collection_name = name,
                        shared_rules_id = contentID
                        )
                collections.append(currentCollection)
    return collections


#loads xml file and returns parsable root of xml
def LoadXML (xmlFile):
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    return root

#loads xml files as object to parse so PARSE can iterate through
currentXML = LoadXML("E:\Documents\Programming\KillTeamBuilder\BScribe Kill Team XML\Adeptus Mechanicus.cat")

#generates list of Rule classes, each of which contains (id, name, text, ruleType)
rules = PARSE.ParseRules(currentXML)
#generates list of Model and Armoury classes
#Model(id, name, cost, chars, rules,sharedRules,links), Armoury(id, name, cost, chars, type)
models, armoury = PARSE.ParseSelectionEntry(currentXML)
#generates list of collections (id, name, contents, type) with contents as ids of sharedrules and armoury items
collections = PARSE.ParseCollections(currentXML)

#generates list of table classes for each function above
sharedRulesList = CreateRuleTable(rules)
modelsList = CreateModelTable(models)
armouryList = CreateArmouryTable(armoury)
collectionList = CreateCollectionTable(collections,armoury)

#loads sqlalchemy engine to communicate with db
engine = create_engine('sqlite:///E:\Documents\Programming\KillTeamBuilder\SQLite DB\DB Files\AdMech.db', echo=True)
#generates db using all available metadata (generated from classes declared using declarative_base() in file)
Base.metadata.create_all(engine)

#start new session in database
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

#looping through list and adding each rule to the database session
#using .merge() to ignore existing unique db entries and only add new data
for rule in sharedRulesList:
    session.merge(rule)
for model in modelsList:
    #loops through output of CreateModelTable
    #adds base stats
    session.merge(model[0])
    #adds characteristics
    session.merge(model[1])
    #loops through list to add unique rules
    for rule in model[2]:
        session.merge(rule)
    #loops through to add shared rules to link table
    for sharedRule in model[3]:
        session.merge(sharedRule)
    #loops to add links to link table
    for link in model[4]:
        session.merge(link)
for equipment in armouryList:
    #adds base armoury data to armoury
    session.merge(equipment[0])
    #adds any relevant profiles, looping for multi profile weapons
    for profile in equipment[1]:
        session.merge(profile)
for collection in collectionList:
    session.merge(collection)

#commit all merge changes to db and close connection
session.commit()