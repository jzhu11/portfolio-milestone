#File Name: Jiebin_Zhu_Final Project.py
#Created by: Jiebin Zhu (Alex)
#Date Written: 6/13/2021

#This program will utilze different datasets related to strokes found from Kaggle and also the CDC website.
#The program will also obtain the sub url information within the CSV file downloaded from the CDC website to scrape for more data and put everything into data frames
#The dataframes will then be used for analysis and answering questions

from urllib import request
from bs4 import BeautifulSoup
import pandas as pd
import os.path
from os import path
from tabulate import tabulate

#creating a function to obtain the ranking for strokes in leading causes of death from the cdc website
#this will return the rank of strokes for a specific state, depending on the sub_url
def stroke_rank(sub_url):
    #the sub_url is obtained from the cdc_strokeDF
    url = "https://www.cdc.gov"+ sub_url
    response = request.urlopen(url)
    html = response.read().decode("utf8")

    #creating a beginning point and ending point for allowing only the top 10 leading cause of death is captured
    causes_index = html.find('Leading Causes of Death</div>')
    start_index = causes_index + len('Leading Causes of Death</div>')
    end_index = html.find('</div></div></div></div><div class="row "><div class="col-md-12 splash-col"></div></div><div')
    #the text_portion now contains the chunk of information tha only contains the top 10 leading cause of deaths
    text_portion = html[start_index:end_index]

    #parsing the text_portion for href tags that contain the disease names
    html_soup = BeautifulSoup(text_portion,"html.parser")
    anchor = html_soup.find_all("a")
    #because each disease has a hyperlink attached to it with its name, it makes obtaining the href tags of them and identifying them possible
    href = [str(link.get('href')) for link in anchor]

    #parsing through all the href tags for the specific state here
    #when the leading cause of death for is identified in the loop, the counter will return that rank
    counter = 0
    for tag in href:
        counter +=1
        if 'stroke' in tag:
            return counter
        else:
            continue

#creating a function to obtain the ranking for heart disease in leading causes of death from the cdc website
#this will return the rank of heart disease for a specific state, depending on the sub_url
def heartDisease_rank(sub_url):
    url = "https://www.cdc.gov"+ sub_url
    response = request.urlopen(url)
    html = response.read().decode("utf8")

    #creating a beginning point and ending point for allowing only the top 10 leading cause of death is captured
    causes_index = html.find('Leading Causes of Death</div>')
    start_index = causes_index + len('Leading Causes of Death</div>')
    end_index = html.find('</div></div></div></div><div class="row "><div class="col-md-12 splash-col"></div></div><div')
    #the text_portion now contains the chunk of information tha only contains the top 10 leading cause of deaths
    text_portion = html[start_index:end_index]

    #parsing the text_portion for href tags that contain the disease names
    html_soup = BeautifulSoup(text_portion,"html.parser")
    anchor = html_soup.find_all("a")
    #because each disease has a hyperlink attached to it with its name, it makes obtaining the href tags of them and identifying them possible
    href = [str(link.get('href')) for link in anchor]

    #parsing through all the href tags for the specific state here
    #when the leading cause of death for is identified in the loop, the counter will return that rank
    counter = 0
    for tag in href:
        counter +=1
        if 'heart_disease' in tag:
            return counter
        else:
            continue

#specifying the csv files to load in
stroke_file = 'healthcare-dataset-stroke-data_modified.csv'
cdc_stroke_file = 'states_stroke_mortality.csv'

#creating column names for those csv files
stroke_file_colNames = ['gender','age','hypertension','heart_disease','ever_married',
'work_type','residence_type','avg_glucose_lvl','bmi','smoking_status','stroke']
cdc_file_colNames = ['year','state','death_rate','death_count','sub_url']

#creating 2 dataframes here from the csv files that were loaded in
strokeDF = pd.read_csv(stroke_file, sep = ',', names = stroke_file_colNames)
cdc_strokeDF = pd.read_csv(cdc_stroke_file, sep = ',', names = cdc_file_colNames)

#dropping the original fields of the dataframe
strokeDF = strokeDF.drop(strokeDF.index[0])
cdc_strokeDF = cdc_strokeDF.drop(cdc_strokeDF.index[0])

#Now a third dataframe will be created that stores the ranks of leading cause of deaths for strokes & heart disease per state 

#Since the program will have to go to the web and pull the data out every single time and takes up time, the ranker dataframe will be imported from a local file 
#if the information has been obtained already.
#If the file doesn't exist in the current directory then it will create the rankerDF dataframe and also go to the web and grab all the information necessary to 
#insert it into the new dataframe here, then the dataframe will be written to the local directory to make this process faster when running it a second time.


#The rankerDF.csv file will be submitted along the submission files, if you want to test this out then either delete the file or move it to another directory
#The following IF statement makes it possible
#If the rankerDF file doesn't exist in the local directory then it will fetch the information from the web, or else it can just read it in
if not path.exists('rankerDF.csv'):

    #creating a dataframe for storing the ranking for leading cause of death in strokes and heart diseases for each state 
    ranker_colNames = ['state','stroke_rank','heart_disease_rank']
    rankerDF = pd.DataFrame(columns = ranker_colNames)
    #naming the states with the 50 states from the cdc_strokeDF
    rankerDF['state'] = cdc_strokeDF['state'][:50]
    #Setting a counter index here to insert the values of the ranks per state (the dataset is already in alphbetical order)
    counter_index = 0

    #going to the web to grab the rankings of Leading causes of death for Stroke and Heart Disease
    #This would take a while to run (about 50 seconds) since it's grabbing the values for all 50 states
    print("Retrieving data from the web...")
    for url in cdc_strokeDF['sub_url'][:50]:
        counter_index +=1
        #calling the 2 functions that were created to obtain the ranks
        s_rank = stroke_rank(url)
        hd_rank = heartDisease_rank(url)
        #storing those ranks in the new dataframe here
        rankerDF.at[counter_index,'stroke_rank'] = s_rank
        rankerDF.at[counter_index,'heart_disease_rank'] = hd_rank
    #storing this DF in the local directory to prevent wasting time in capturing the data off the web again
    rankerDF.to_csv('rankerDF.csv',index = False)
else:
    #loading in the rankerDF from the local directory as a dataframe
    rankerDF = pd.read_csv('rankerDF.csv', sep = ',')


#the task for creating the ranks for the leading causes of death for Stroke and Heart Diseases is complete so the sub_url column is no longer needed here.
cdc_strokeDF = cdc_strokeDF.drop(columns = ['sub_url'])
#dropping the last row which is completely blank
cdc_strokeDF = cdc_strokeDF.drop([351])

#converting the death rate and death count to its approriate data type
cdc_strokeDF.death_rate = cdc_strokeDF.death_rate.astype('float')
#removing the commas from the death_count column first before converting its type
cdc_strokeDF['death_count'] = cdc_strokeDF['death_count'].str.replace(',','')
cdc_strokeDF.death_count = cdc_strokeDF.death_count.astype('int')



#-----The cleaning and splitting of cdc_strokeDF is complete here and will move on with cleaning the strokeDF

#The only column that contains bad data in this dataframe is the "bmi" column
#replacing all NA values in the bmi column with 0s
strokeDF['bmi'] = strokeDF['bmi'].fillna(0)

#converting numeric fields to its appropriate type
#age here is a float because there are also babies and toddlers included within the data set so their age is a denoted with an additional decimal values for months
strokeDF.age = strokeDF.age.astype('float')
strokeDF.hypertension = strokeDF.hypertension.astype('int')
strokeDF.heart_disease = strokeDF.heart_disease.astype('int')
strokeDF.avg_glucose_lvl = strokeDF.avg_glucose_lvl.astype('float')
strokeDF.bmi = strokeDF.bmi.astype('float')
strokeDF.stroke = strokeDF.stroke.astype('int')

#The cleaning of the strokeDF dataset is now complete

#------Question time

#Q1: What's the avg and median stroke death count/death rate for all 50 states in all the different years listed within the data set for strokes
#Grouping the dataframe by Years here and obtaining the mean/median of death counts/death_rates in in all the states
Q1DF_mean = cdc_strokeDF.groupby(['year']).mean()
Q1DF_med = cdc_strokeDF.groupby(['year']).median()

#displaying the data out nicely
print("Mean")
print(tabulate(Q1DF_mean, headers = 'keys', tablefmt = 'psql'))
print("\nMedian")
print(tabulate(Q1DF_med, headers = 'keys', tablefmt = 'psql'))



#Q2: What's the most common ranking for stroke and heart diseases as a leading cause of death in the US?
#creating a blank dataframe that allows the transfer of values from the dataset
Q2DF = pd.DataFrame(columns = ['stroke_rank','heart_disease_rank'])

#transferring the values to the new dataframe
Q2DF['stroke_rank'] = rankerDF['stroke_rank'].mode()
Q2DF['heart_disease_rank'] = rankerDF['heart_disease_rank'].mode()

#displaying the data out nicely
print("\nRanking")
print(tabulate(Q2DF, headers = 'keys', tablefmt = 'psql'))



#Q3: What's the total amount of male/female who has had a stroke before, based on their work type? How about heart disease?
#creating a blank dataframe that allows the transfer of values from the dataset
Q3DF = pd.DataFrame(columns = ['gender','work_type','stroke_count'])

#transferring the values to the new dataframe
Q3DF['gender'] = strokeDF['gender']
Q3DF['work_type'] = strokeDF['work_type']
Q3DF['stroke_count'] = strokeDF['stroke']

#grouping the attributes out there and summing them up for the count
#the summation function can be used here because the "stroke" field only contains 1s and 0s
Q3DF = Q3DF.groupby(['work_type','gender']).sum()
#displaying the data out nicely
print("")
print(tabulate(Q3DF, headers = 'keys', tablefmt = 'psql'))

#Doing the same thing as above, but switching the disease type from stroke to heart_disease
Q3_1DF = pd.DataFrame(columns = ['gender','work_type','HD_count'])

Q3_1DF['gender'] = strokeDF['gender']
Q3_1DF['work_type'] = strokeDF['work_type']
Q3_1DF['HD_count'] = strokeDF['heart_disease']

Q3_1DF = Q3_1DF.groupby(['work_type','gender']).sum()
print("")
print(tabulate(Q3_1DF, headers = 'keys', tablefmt = 'psql'))

#This also answers another research question of:
#What is the most common characteristics that patients who’ve already had a stroke compared to the ones who didn’t have one yet?
#Answer: Work_type = Private
#Maybe Private work can be stressful


#Q4: What is the median average glucose level for each gender varying on if they were a smoker and also the type of residence they live in?
#creating a blank dataframe that allows the transfer of values from the dataset
Q4DF = pd.DataFrame(columns = ['gender','smoking_status','residence_type','avg_glucose_lvl'])

#transferring the values to the new dataframe
Q4DF['gender'] = strokeDF['gender']
Q4DF['smoking_status'] = strokeDF['smoking_status']
Q4DF['residence_type'] = strokeDF['residence_type']
Q4DF['Med_avg_glucose_lvl'] = strokeDF['avg_glucose_lvl']

#grouping the attributes within this newly created dataframe and obtain the median from this
Q4DF = Q4DF.groupby(['residence_type','smoking_status','gender']).median()
#displaying the data out nicely
print("")
print(tabulate(Q4DF, headers = 'keys', tablefmt = 'psql'))


