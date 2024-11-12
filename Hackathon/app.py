from flask import Flask, render_template, request
import joblib
import pandas as pd
import requests
import json
from datetime import datetime
from normalize import normalize
from normalize import recommend_location
from recommend import recommend_location_onbudget


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/cost')
def form():
    return render_template('cost_est.html')

@app.route('/more', methods=['POST', 'GET'])
def more():
    if request.method == 'POST':
        budget = request.form['budget']
        recommend = recommend_location_onbudget(int(budget))
        if recommend[0][0]==1:
            flight = 'Business'
        elif recommend[0][0]==2:
            flight = 'Economy'
        return render_template('more.html', place = recommend[0][2], flight = flight, hotel = recommend[0][1])
    return render_template('more.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        values = request.form
        print('input: ')
        values = values.to_dict()
        print(values)
        source = 'BLR'
        if(values['destination']=='Delhi'):
            dest = 'DEL'
        elif(values['destination']=='Mumbai'):
            dest = 'BOM'
        elif(values['destination']=='Chennai'):
            dest = 'MAA'
        elif(values['destination']=='Hyderabad'):
            dest = 'HYD'
        checkin = datetime.strptime(values['startDate'], "%Y-%m-%d").strftime("%m/%d/%Y")
        checkout = datetime.strptime(values['endDate'], "%Y-%m-%d").strftime("%m/%d/%Y")
        flightclass = values['flight']
        url = 'https://api.flightapi.io/roundtrip/63ebc4550e9442819e3f5963/' + source + '/' + dest + '/' + values['startDate'] + '/' + values['endDate'] + '/1/0/0/' + flightclass + '/INR'
        response = requests.get(url)
        output = response.json()
        flight_cost = output['fares'][0]['price']['totalAmount']
        food = joblib.load('model_pickle_food.pkl')
        transport = joblib.load('model_pickle_city.pkl')
        incidental = joblib.load('model_pickle_incidental.pkl')
        if(flightclass=='Economy'):
            flightclass=1.0
        elif(flightclass=='Business'):
            flightclass=2.0
        hotelurl = "https://skyscanner50.p.rapidapi.com/api/v1/searchHotel"
        # entityId for Mumbai: 27539520
        # entityId for Delhi: 44292309
        # chennai: 32575954
        # hyderabad: 27542764
        if values['destination']=='Mumbai':
            entity = '27539520'
        elif values['destination']=='Delhi':
            entity = '44292309'
        elif values['destination']=='Chennai':
            entity = '32575954'
        elif values['destination']=='Hyderabad':
            entity = '27542764'
        querystring = {"entityId":entity,"checkin":values['startDate'],"checkout":values['endDate'],"stars[0]":values['hotel'],"currency":"INR","countryCode":"IN"}
        # 4d2f575afcmsh21cca7bd5e1fa21p1c4736jsn0eafa9ab0016
        headers = {
            "X-RapidAPI-Key": "73cc50260bmshb4ad531562bd36fp1c534fjsn4463c0bf22b8",
            "X-RapidAPI-Host": "skyscanner50.p.rapidapi.com"
        }
        response = requests.request("GET", hotelurl, headers=headers, params=querystring)
        t = response.json()
        hotel_cost = int(t['data']['hotels'][0]['price'][2:].replace(',',''))
        input = normalize([int(values['age']), checkin, checkout, flightclass, float(values['hotel']), values['gender'], values['purpose'], values['destination']])
        X = pd.DataFrame([[input[0],input[1],input[2],input[3],input[4],input[8],input[12],input[5],input[9],input[10],input[11],input[13],input[14],input[15],input[16]]], columns = ['Age', 'start_date', 'end_date', 'Flight Class', 'Hotel Fare', 'number of days', 'Gender_Female' , 'Gender_Male', 'Purpose_Business', 'Purpose_Business Leisure', 'Purpose_Leisure', 'Destination_Chennai', 'Destination_Delhi', 'Destination_Hyderabad', 'Destination_Mumbai'])
        food_cost = round(food.predict(X)[0])/10
        transport_cost = round(transport.predict(X)[0])
        incidental_cost = round(incidental.predict(X)[0])
        total_cost  = hotel_cost + flight_cost + food_cost + transport_cost + incidental_cost
        i,j,k,calculated_budget,rstar,rfclass = recommend_location(input, total_cost)
        print(type(j), type(rfclass), type(rstar))
        if j==1:
            j='Business'
        elif j==2:
            j='Economy'
        if rfclass==1:
            rfclass='Business'
        elif rfclass==2:
            rfclass='Economy'
    return render_template("total_cost.html", hotel_cost = hotel_cost, flight_cost = flight_cost, food_cost = food_cost, transport_cost = transport_cost, incidental_cost = incidental_cost, total_cost = total_cost, place_recommend = i, flight_recommend = j, hotel_recommend = k, flight20 = rfclass, hotel20 = rstar)

if __name__=='__main__':
    app.run(debug=True)