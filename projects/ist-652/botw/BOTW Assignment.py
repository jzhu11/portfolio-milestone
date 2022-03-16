#Program Name: Jiebin_Zhu_HW2.py
#Created by: Jiebin Zhu (Alex)
#Written on: May 29th, 2021


#This program will collect data from an API that contains the information for a very popular game called "The Legends of Zelda: Breath of the Wild"
#This information will be put into dataframes for analysis
#Several data frames will be created based on its category
#The end product of this program is to help understand and learn the game better.

import pandas as pd
import json
import urllib.request
from tabulate import tabulate

#specifying the api
zelda_url = "https://botw-compendium.herokuapp.com/api/v2"

#This portion of the program will return an error message if the access of the API gets cut off or runs into some weird errors
try:
	response = urllib.request.urlopen(zelda_url)
except urllib.error.URLError as e:
    if hasattr(e, 'reason'):
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
        print("Pleas try again in a few minutes and make sure your internet connection is available.")
    elif hasattr(e, 'code'):
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
        print("Pleas try again in a few minutes and make sure your internet connection is available.")
else:
	# the url request was successful then now it will convert that response into a string
    json_string = response.read().decode('utf-8')

    #this portion will convert that string into a json format
    hyrule_kingdom = json.loads(json_string)

    #defining the functions to gather data from the API, making the code cleaner when operating
    def food(hyrule_json):
        food_list = []
        all_food = hyrule_json['data']['creatures']['food']
        for food in all_food:
            food_list.append(food)
        return food_list

    def material(hyrule_json):
        material_list = []
        all_materials = hyrule_json['data']['materials']
        for material in all_materials:
            material_list.append(material)
        return material_list

    def equipment(hyrule_json):
        equip_list = []
        all_equip = hyrule_json['data']['equipment']
        for equip in all_equip:
            equip_list.append(equip)
        return equip_list

    def monster(hyrule_json):
        mob_list = []
        all_mobs = hyrule_json['data']['monsters']
        for mob in all_mobs:
            mob_list.append(mob)
        return mob_list

    #running the functions to obtain the data from the JSON of the game information 
    hyrule_food = food(hyrule_kingdom)
    hyrule_material = material(hyrule_kingdom)
    hyrule_equipment = equipment(hyrule_kingdom)
    hyrule_mobs = monster(hyrule_kingdom)

    #creating column names for the dataframes
    consumables_DF_names = ['name','cooking_effect','hearts_recovered','category','common_locations','description','image','id']
    equipment_DF_names = ['name','attack','defense','common_locations','description','image','id']
    mob_DF_names = ['name', 'drops', 'common_locations', 'description','image','id']


    #generating the 3 different dataframes to obtain some statistics on the different component of the game itself

    consumables_DF = pd.DataFrame(hyrule_food, columns = consumables_DF_names)
    consumables_DF = consumables_DF.append(hyrule_material)

    equipment_DF = pd.DataFrame(hyrule_equipment, columns = equipment_DF_names)
    mob_DF = pd.DataFrame(hyrule_mobs, columns = mob_DF_names)


    #Q1. How many items have attack points greater than 30? What are they? Where are they? What's the median atk value for all the weapons?
    #Context: In the game, these weapons are considered high damage given the HP pool of some enemies.

    #Creating a function that takes in the equipment dataframe and filter it out by a specified attack value
    #It will print out a statement with the actual count of how many weapons will exceed the atk value
    #It will also return the filtered dataframe with the name, atk value, and some common locations in where the item is located
    #Note: Some items will not have a common location since those items are usually obtained via NPC (Non-Playable Characters) interactions or Quest Items that would disappear
    def attack_equipment(df, atk_point):
        #filtering the dataframe by the atk value of the weapon
        filtered_attack_equipment = df[df['attack'] > atk_point]

        #creating a new dataframe that will capture only the filtered information, leaving out unncessary information
        weapon_col = ['name','attack','common_locations']
        weapons = pd.DataFrame(columns=weapon_col)
        weapons['name'] = filtered_attack_equipment['name']
        weapons['attack'] = filtered_attack_equipment['attack']
        weapons['common_locations'] = filtered_attack_equipment['common_locations']
        weapons = weapons.sort_values(by = ['attack'])

        #counting the number of weapons that are over the specified atk value
        #AND also counting the total number of weapons to provide a baseline for users to understand how many weapons are in the game
        count_condition = 0
        count_total = 0
        for n in weapons['name']:
            count_condition +=1
        #this counts the total weapons to exclude the shields since shields have an attack value of 0
        for x in df[df['attack'] > 0]['name']:
            count_total +=1
        print("There are {} weapons out of {} greater than {}. Here's their information:\n".format(count_condition,count_total,atk_point))
        print("The median out of all the weapons is: {}".format(df[df['attack'] > 0]['attack'].median()))
        
        #returning the weapons dataframe at the end of the function
        return weapons


    #The "one-hit obliterator" is a quest item that literally takes any monster out in one hit, hence the really high attack value.
    #Displaying the dataframe in a nicer way.
    wep_over30 = attack_equipment(equipment_DF, 30)
    print(tabulate(wep_over30, headers = 'keys', tablefmt = 'psql'))


    #Q2 What's the mean, median, and mode for materials that's used for healing purposes? How about for the ones above a certain hp recovery threshold?
    #Creating a function that returns the measure of central tendency for materials that provide hp recovery in the game. 
    #The function will allow the recovery amount to be specified since the game has a lot of items that recover a low amount of HP, but that could heavily skew the data.
    def hp_central_tendency(df, hp_up):
        #filtering the df with only materials that provides over a specified amount hearts when consumed
        filtered_hp = df[df['hearts_recovered'] > hp_up]
        
        #setting the df name with the correct dataframe
        df.name = get_df_name(df)
        #creating a new dataframe that will capture only the filtered information, leaving out unncessary information
        hp_col = ['DF_name','mean','median','mode']
        hp = pd.DataFrame(columns=hp_col)

        #specifying the values of this new dataframe with the central tendency infromation
        hp['DF_name'] = df.name
        hp['mean'] = filtered_hp['hearts_recovered'].mean()
        hp['median'] = filtered_hp['hearts_recovered'].median()
        hp['mode'] = filtered_hp['hearts_recovered'].mode()

        #Since the information will just end up repeating, this is returning only the first row for displaying purposes.
        return hp.iloc[0]

    #this function gets the name of the any dataframe
    #got this from https://stackoverflow.com/questions/54137694/how-to-print-dataframe-name-in-title-of-a-plot
    def get_df_name(df):
        name =[x for x in globals() if globals()[x] is df][0]
        return name

    #displaying the results
    print(hp_central_tendency(consumables_DF, 0))
    print(hp_central_tendency(consumables_DF,1))



    #Q3 What are the monster drops for Moblins, Lizalfos, Octoroks, and some common locations they are in?

    #Creating a function that filters the dataframe out by a monster species and returns that dataframe with the monster name, drops, and common locations they are in
    #If they don't have a common location in the game that means that's either a rare monster or they exist only in specific dungeons
    #It's also common for monsters to not have drops in the game, hence the blank values
    def mob_drop(df, mob_species_name):
        #filtering out the df with the mob specifies name
        filtered_mob = df[df['name'].str.contains(mob_species_name)]

        #creating a new dataframe to use for a neater display later
        mob_col = ['name','drops','common_locations']
        mobs = pd.DataFrame(columns=mob_col)

        #transferring the values over from the filtered df to the new df
        mobs['name'] = filtered_mob['name']
        mobs['drops'] = filtered_mob['drops']
        mobs['common_locations'] = filtered_mob['common_locations']

        return(mobs)

    #running the function and saving them to its corresponding variables
    moblin_drop = mob_drop(mob_DF, "moblin")
    lizalfos_drop = mob_drop(mob_DF, "lizalfos")
    octorok_drop = mob_drop(mob_DF, "octorok")

    #displaying the result nicely in a well formatted way
    print(tabulate(moblin_drop, headers = 'keys', tablefmt = 'psql'))
    print(tabulate(lizalfos_drop, headers = 'keys', tablefmt = 'psql'))
    print(tabulate(octorok_drop, headers = 'keys', tablefmt = 'psql'))
