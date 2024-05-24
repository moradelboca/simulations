import numpy as np
import pandas as pd

weeks = 18 #Default 18
initial_stock = 28 #Default 28
units_per_req = 15 #Default 15.
keeping_cost = 10 #Per unit, per week. Default 10
request_cost = 200 #Default 200.
oos_cost = 200 #Out of stock per unit. Default 50 
price = 100 #Price per unit. Default 100
weeks_b = 15
units_per_req_b = 15
min_stock_for_request = 5
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

    return montecarlo_table

def montecarloB():
    units_per_req = units_per_req_b
    weeks = weeks_b
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
                row['gains'] += (row['article demand'] + row['stock'])* price
                oos_quantity = np.abs(row['stock'])
                row['stock'] = 0
                row['out of stock cost'] = oos_quantity * oos_cost
            else:
                row['gains'] += row['article demand'] * price
                row['keeping cost'] = row['stock'] * keeping_cost
            if(request_tmr):
                row['request'] = True
                request_tmr = False
                row['rnd2'] = round(np.random.uniform(high=0.99), 2)
                row['delivery advance'] = map_in_interval(row['rnd2'], advance_table)
                row['delivery day'] = days[int((days.index(day)+7-row['delivery advance'])%7)]
                row['request cost'] += request_cost
            if(row['stock'] <= min_stock_for_request and row['delivery day'] == '-'): request_tmr = True
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

    return montecarlo_table

def generateBothCSV():
    print('Generando el csv del punto A')
    montecarloA().to_csv("./TP3/montecarloA.csv")    
    print('Generado!')
    print('Generando el csv del punto B')
    montecarloB().to_csv("./TP3/montecarloB.csv")    
    print('Generado!')
    print('Puedes ver los archivos generados en la carpeta del proyecto.')

def menu():
    print('Bienvenido al TP3')
    print('1. Generar CSVs')
    print('2. Modificar parametros')
    print('3. Salir')
    option = input('Ingrese una opción: ')
    if(option == '1'):
        generateBothCSV()
    elif(option == '2'):
        menu_modify()
    elif(option == '3'):
        print('Hasta luego!')
    else:
        print('Opción incorrecta')
        menu()

def menu_modify():
    print('Modificar parametros')
    print('1. Modificar semanas')
    print('2. Modificar stock inicial')
    print('3. Modificar unidades por requerimiento')
    print('4. Modificar costo de mantenimiento')
    print('5. Modificar costo de pedido')
    print('6. Modificar costo de faltante')
    print('7. Modificar precio')
    print('8. Modificar semanas para el punto B')
    print('9. Modificar unidades por requerimiento para el punto B')
    print('10. Modificar stock minimo para hacer un pedido en el punto B')
    print('11. Volver al menu principal')
    option = input('Ingrese una opción: ')
    if(option == '1'):
        global weeks
        weeks = int(input('Ingrese la cantidad de semanas: '))
        menu_modify()
    elif(option == '2'):
        global initial_stock
        initial_stock = int(input('Ingrese el stock inicial: '))
        menu_modify()
    elif(option == '3'):
        global units_per_req
        units_per_req = int(input('Ingrese las unidades por requerimiento: '))
        menu_modify()
    elif(option == '4'):
        global keeping_cost
        keeping_cost = int(input('Ingrese el costo de mantenimiento: '))
        menu_modify()
    elif(option == '5'):
        global request_cost
        request_cost = int(input('Ingrese el costo de pedido: '))
        menu_modify()
    elif(option == '6'):
        global oos_cost
        oos_cost = int(input('Ingrese el costo de faltante: '))
        menu_modify()
    elif(option == '7'):
        global price
        price = int(input('Ingrese el precio: '))
        menu_modify()
    elif(option == '8'):
        global weeks_b
        weeks_b = int(input('Ingrese la cantidad de semanas para el punto B: '))
        menu_modify()
    elif(option == '9'):
        global units_per_req_b
        units_per_req_b = int(input('Ingrese las unidades por requerimiento para el punto B: '))
        menu_modify()
    elif(option == '10'):
        global min_stock_for_request
        min_stock_for_request = int(input('Ingrese el stock minimo para hacer un pedido en el punto B: '))
        menu_modify()
    elif(option == '11'):
        menu()
    else:
        print('Opción incorrecta')
        menu_modify()

if __name__ == '__main__':
    menu()