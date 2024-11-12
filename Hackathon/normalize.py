from datetime import datetime, timedelta
import joblib
import pandas as pd

def number_of_days(start_date, end_date):
    startdate_format = "%m/%d/%Y" if "/" in start_date else "%m-%d-%Y"
    enddate_format = "%m/%d/%Y" if "/" in end_date else "%m-%d-%Y"
    

    start_date = datetime.strptime(start_date, startdate_format)
    end_date = datetime.strptime(end_date, enddate_format)
    delta = end_date - start_date
    return delta.days

def normalize(input):
    # input = [25,'02/13/2023','02/16/2023',2.0,3.0,'Male','Leisure','Chennai']
    #age
    min_age = 18
    max_age = 80
    input[0]=1+(((input[0]-min_age)/(max_age-min_age))*(10-1))
    #dates
    input.append(number_of_days(input[1],input[2]))
    input[1] = number_of_days('1/10/2005',input[1])
    misd = 0.0
    masd = 7295.0
    input[1] = 0+(((input[1]-misd)/(masd-misd))*(1000))
    input[2] = number_of_days('1/1/2005',input[2])
    mied = 0.0
    maed = 7298.0
    input[2] = 0+(((input[2]-mied)/(maed-mied))*(1000))
    #gender
    if input[5]=='Male':
        input[5]= 1 
    else:
        input[5]= 0
    #Purpose
    input.append(0)
    input.append(0)
    input.append(0)
    if input[6]=='Leisure':
        input[11]=1
    elif input[6]=='Business Leisure':
        input[10]=1
    else:
        input[9]=1
    input.append(0)
    # gender hot encoding 
    input[12] = 1 if input[5]==0 else 0
    #Dest
    input.append(0)
    input.append(0)
    input.append(0)
    input.append(0)
    if input[7]=='Chennai':
        input[13]=1
    elif input[7]=='Delhi':
        input[14]=1
    elif input[7]=='Hyderabad':
        input[15]=1
    else:
        input[16]=1
    return input


def recommend_location(input,budget):
    dests = ['Chennai','Delhi','Hyderabad','Mumbai']
    flag = 0
    dests.remove(input[7])
    food = joblib.load('model_pickle_food.pkl')
    transport = joblib.load('model_pickle_city.pkl')
    incidental = joblib.load('model_pickle_incidental.pkl')
    for i in dests:
        d=[0,0,0,0]
        if input[7]=='Chennai':
            d[0]=1
        elif input[7]=='Delhi':
            d[1]=1
        elif input[7]=='Hyderabad':
            d[2]=1
        else:
            d[3]=1
        for j in range(1,4):
            for k in range(5,1,-1):
                calculated_budget = transport.predict(pd.DataFrame([[input[0],input[1],input[2],j,k,input[8],input[12],input[5],input[9],input[10],input[11],d[0],d[1],d[2],d[3]]]))+incidental.predict(pd.DataFrame([[input[0],input[1],input[2],j,k,input[8],input[12],input[5],input[9],input[10],input[11],d[0],d[1],d[2],d[3]]]))+food.predict(pd.DataFrame([[input[0],input[1],input[2],j,k,input[8],input[12],input[5],input[9],input[10],input[11],d[0],d[1],d[2],d[3]]]))
                if (calculated_budget<=budget*0.2 + budget) and flag==0:
                    rstar = k
                    rfclass = j
                    print("recommendation!!! ",i,j,k,calculated_budget)
                    flag=1
                elif(calculated_budget<=budget):
                    print("your plan--",i,j,k,calculated_budget)
                    return i,j,k,calculated_budget,rstar,rfclass
                