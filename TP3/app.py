import numpy as np
import pandas as pd

weeks = 18 #Default 18
initial_stock = 28 #Default 28
units_per_req = 15 #Default 15.
keeping_cost = 10 #Per unit, per week. Default 10
request_cost = 200 #Default 200.
oos_cost = 200 #Out of stock per unit. Default 50 
price = 100 #Price per unit. Default 100
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

df_daily_demand = pd.DataFrame(data=[[0, 0.05],
                                    [1, 0.20],
                                    [2, 0.40],
                                    [3, 0.15],
                                    [4, 0.10],
                                    [5, 0.05],
                                    [6, 0.05]],
                            columns=['value', 'probability'])

df_request_advance = pd.DataFrame(data=[[0, 0.10],
                                        [1, 0.25],
                                        [2, 0.60],
                                        [3, 0.05]],
                                columns=['value', 'probability'])

def prob_to_intervals(prob_table):
    intervals_table = pd.DataFrame(columns=['start', 'end', 'value'])
    start = 0.0
    for index, row in prob_table.iterrows():
        end = start+row['probability']
        interval_row = {'start':start, 'end':end,'value':row['value']}
        start = end
        intervals_table.loc[len(intervals_table.index)] = interval_row
    return intervals_table

advance_table = prob_to_intervals(df_request_advance)
daily_demand_table = prob_to_intervals(df_daily_demand)

def map_in_interval(value, table):
    row = table[(table['start'] <= value) & (table['end'] > value)]
    return row.iloc[0, 2]

def montecarloA():
    row = {'week': '-',
            'total days': 0,
            'day': '-',
            'rnd1': '-',
            'article demand': '-',
            'stock': initial_stock, 
            'request': '-',
            'rnd2': '-',
            'delivery advance': '-',
            'delivery day': '-',
            'gains': 0,
            'out of stock cost': 0,
            'request cost': 0,
            'keeping cost': 0,
            'total cost': 0
        }

    montecarlo_table = pd.DataFrame(data=[row])
    
    for week in range(weeks):
        row['week'] = week+1
        for day in days:
            if(day == 'Monday'):
                row['request'] = True
                row['rnd2'] = round(np.random.uniform(high=0.99), 2)
                row['delivery advance'] = map_in_interval(row['rnd2'], advance_table)
                row['delivery day'] = days[6-int(row['delivery advance'])]
                row['request cost'] += request_cost
            if(day == row['delivery day']):
                row['stock'] += units_per_req
                row['delivery day'] = '-'
            row['total days'] += 1
            row['day'] = day
            row['rnd1'] = round(np.random.uniform(high=0.99), 2)
            row['article demand'] = map_in_interval(row['rnd1'], daily_demand_table)
            row['stock'] -= row['article demand']
            if(row['stock'] < 0):
                row['gains'] += (row['article demand'] + row['stock'])* price
                oos_quantity = np.abs(row['stock'])
                row['stock'] = 0
                row['out of stock cost'] = oos_quantity * oos_cost
            else:
                row['gains'] += row['article demand'] * price
                row['keeping cost'] = row['stock'] * keeping_cost
            row['total cost'] += row['out of stock cost'] + row['request cost'] + row['keeping cost']
            montecarlo_table.loc[len(montecarlo_table.index)] = row
            # Reset all data
            row['rnd1'] = '-'
            row['article demand'] = 0
            row['request'] = '-' 
            row['rnd2'] = '-'
            row['delivery advance'] = '-'
            row['out of stock cost'] = 0
            row['request cost'] = 0
            row['keeping cost'] = 0

    montecarlo_table.to_csv("./TP3/montecarloA.csv")

def montecarloB():
    units_per_req = 15
    weeks = 15
    row = {'week': '-',
            'total days': 0,
            'day': '-',
            'rnd1': '-',
            'article demand': '-',
            'stock': initial_stock, 
            'request': '-',
            'rnd2': '-',
            'delivery advance': '-',
            'delivery day': '-',
            'out of stock cost': 0,
            'request cost': 0,
            'keeping cost': 0,
            'total cost': 0
        }

    montecarlo_table = pd.DataFrame(data=[row])
    request_tmr = False
    for week in range(weeks):
        row['week'] = week+1
        for day in days:
            if(day == row['delivery day']):
                row['stock'] += units_per_req
                row['delivery day'] = '-'
            row['total days'] += 1
            row['day'] = day
            row['rnd1'] = round(np.random.uniform(high=0.99), 2)
            row['article demand'] = map_in_interval(row['rnd1'], daily_demand_table)
            row['stock'] -= row['article demand']
            if(row['stock'] < 0):
                oos_quantity = np.abs(row['stock'])
                row['stock'] = 0
                row['out of stock cost'] = oos_quantity * oos_cost
            else:
                row['keeping cost'] = row['stock'] * keeping_cost
            if(request_tmr):
                row['request'] = True
                request_tmr = False
                row['rnd2'] = round(np.random.uniform(high=0.99), 2)
                row['delivery advance'] = map_in_interval(row['rnd2'], advance_table)
                row['delivery day'] = days[int((days.index(day)+7-row['delivery advance'])%7)]
                row['request cost'] += request_cost
            if(row['stock'] <= 5 and row['delivery day'] == '-'): request_tmr = True
            row['total cost'] += row['out of stock cost'] + row['request cost'] + row['keeping cost']

            montecarlo_table.loc[len(montecarlo_table.index)] = row
            # Reset all data
            row['rnd1'] = '-'
            row['article demand'] = 0
            row['rnd2'] = '-'
            row['request'] = '-'
            row['delivery advance'] = '-'
            row['out of stock cost'] = 0
            row['request cost'] = 0
            row['keeping cost'] = 0

    montecarlo_table.to_csv("./TP3/montecarloB.csv")

if __name__ == '__main__':
    print('Generando el csv del punto A')
    montecarloA()
    print('Generado!')
    print('Generando el csv del punto B')
    montecarloB()
    print('Generado!')
    print('Puedes ver los archivos generados en la carpeta del proyecto.')