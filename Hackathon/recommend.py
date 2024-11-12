import joblib
import pandas as pd

def recommend_location_onbudget(input_budget):
  Flight_cost = [14000,9000,6000]
  Hotel_cost = [8000*3,5000*3,3000*3,2000*3]
  result = []
  dest_prev = []
  n = 0
  for j in range(1,4):
    input_budget-=Flight_cost[j-1]
    for k in range(5,3,-1):
      input_budget-=Hotel_cost[5-k]
      model = joblib.load('recommend.pkl')
      dest = model.predict(pd.DataFrame([[input_budget]]))
      dest_prev.append(dest[0])
      if dest[0] not in dest_prev or n==0:
        n=1
        result.append([j,k,dest[0]])
      input_budget+=Hotel_cost[5-k]
    input_budget+=Flight_cost[j-1]
  return result