from values import *
import numpy as np
import pandas as pd
from pprint import pprint
from progressbar import ProgressBar
from excel_manager import ExcelManager


class Client:
    id = 0

    def __init__(self, arrival_time, service):
        self.arrival_time = arrival_time
        self.survey_time = None
        self.status = 'WA'  # Waiting
        self.service = service
        self.node = None
        Client.id += 1

    def __repr__(self):
        return f'Client: {self.service} - {self.status} - {self.node} - {self.arrival_time}'

    @classmethod
    def get_id(cls):
        return cls.id

    def attend(self, node):
        self.status = 'BA'  # Being attended
        self.node = node

    def survey(self, survey_time):
        self.status = 'SU'
        self.service = 'survey'
        self.node = None


def truncate(num, decimals=4):
    return int(num * (10**decimals)) / (10**decimals)


def logaritmicRND(rnd, freq):
    return truncate((-60/freq) * np.log(1 - rnd))


def uniformRND():
    return truncate(np.random.uniform(high=0.9999))


def search_next_event(row, manage_survey=False):
    next_event = {
        'type': None,
        'name': None,
        'time': None,
        'node': None
    }
    # Search for the next event in the starting events
    for event in row['starting_events']:
        if (not next_event['name'] or row['starting_events'][event]['rel_time'] < next_event['time']):
            next_event['type'] = 'start'
            next_event['name'] = event
            next_event['time'] = row['starting_events'][event]['rel_time']
    if (row['N'] == 0):
        return next_event
    # Search for the next event in the ending events
    for event in row['ending_events']:
        for i in range(len(row['ending_events'][event]['services'])):
            # Check if there is an ending event
            if (row['ending_events'][event]['services'][i] != None and row['ending_events'][event]['services'][i] < next_event['time']):
                next_event['type'] = 'end'
                next_event['name'] = event
                next_event['time'] = row['ending_events'][event]['services'][i]
                next_event['node'] = i
    # Search for the next event in the survey
    if manage_survey and row['survey']['state'] == 'busy' and row['survey']['duration']['rel_time'] < next_event['time']:
        next_event['type'] = 'survey'
        next_event['name'] = 'survey'
        next_event['time'] = row['survey']['duration']['rel_time']
    return next_event


def event_handling(row, manage_survey=False):
    next_event = search_next_event(row, manage_survey)
    # Get the service frequencies
    row['event'] = next_event['type'] + ' ' + next_event['name']
    if (next_event['type'] == 'end'):
        row['event'] += ' ' + str(next_event['node'])
    row['clock'] = next_event['time']
    row['N'] += 1
    # Arrival event
    if (next_event['type'] == 'start'):
        arrival_event(row, next_event['name'])
    # Ending event
    elif (next_event['type'] == 'end'):
        ending_event(row, next_event['name'], next_event['node'])
        # Survey event
        survey_start_event(row, manage_survey)
    elif (next_event['type'] == 'survey'):
        survey_end_event(row)
    return row


def arrival_event(row, event_name):
    for s in services:
        if (s.name == event_name):
            service = s
    # Generate next arival event
    row['starting_events'][event_name]['rnd'] = uniformRND()
    row['starting_events'][event_name
                           ]['abs_time'] = logaritmicRND(row['starting_events'][event_name]['rnd'], service.arrival_freq)
    row['starting_events'][event_name]['rel_time'] = truncate(
        row['starting_events'][event_name]['abs_time'] + row['clock'])
    # Generate ending event
    row['ending_events'][event_name]['rnd'] = uniformRND()
    row['ending_events'][event_name]['abs_time'] = logaritmicRND(
        row['ending_events'][event_name]['rnd'], service.service_freq)
    # Check if there is a free node
    free_node = None
    for i in range(service.nodes):
        if (row['service_states'][event_name][i]['state'] == 'free'):
            free_node = i
            break
    # If there is a free node, assign the client to it
    if (free_node != None):
        row['service_states'][event_name][free_node]['state'] = 'busy'
        row['service_states'][event_name][free_node]['starting_time'] = row['clock']
        row['ending_events'][event_name]['services'][free_node] = truncate(
            row['clock'] + row['ending_events'][event_name]['abs_time'])
        client = Client(row['clock'], event_name)
        client.attend(free_node)
        row['clients'].append(client)
    # If there is no free node, the client will wait
    else:
        row['total_queued_clients'][event_name] += 1
        row['service_states'][event_name]['queue'] += 1
        row['clients'].append(Client(row['clock'], event_name))


def ending_event(row, event_name, event_node, include_survey=False):
    for s in services:
        if (s.name == event_name):
            service = s
    # Free the node
    row['service_states'][event_name
                          ][event_node]['state'] = 'free'
    row['service_states'][event_name
                          ][event_node]['starting_time'] = None
    row['ending_events'][event_name
                         ]['services'][event_node] = None
    # Search for the client who has been attended
    for client in row['clients']:
        if (client.status == 'BA' and client.service == event_name and client.node == event_node):
            client.survey(row['clock'])
            break
    # Check if there is a client in the queue
    if (row['service_states'][event_name]['queue'] > 0):
        # There is one client waiting
        row['service_states'][event_name]['queue'] -= 1
        row['service_states'][event_name
                              ][event_node]['state'] = 'busy'
        row['service_states'][event_name
                              ][event_node]['starting_time'] = row['clock']
        # Generate new ending event
        row['ending_events'][event_name]['rnd'] = uniformRND()
        row['ending_events'][event_name]['abs_time'] = logaritmicRND(
            row['ending_events'][event_name]['rnd'], service.service_freq)
        row['ending_events'][event_name]['services'][event_node] = truncate(
            row['clock'] + row['ending_events'][event_name]['abs_time'])
        # Search for client who has waited the longest
        for client in row['clients']:
            if (client.status == 'WA' and client.service == event_name):
                client.attend(event_node)
                time_waited = row['clock'] - client.arrival_time
                row['waiting_time'][event_name] += time_waited
                break


def survey_start_event(row, manage_survey=False):
    if not manage_survey:
        # Looks for the client and removes it from the list
        for client in row['clients']:
            if (client.status == 'SU'):
                row['clients'].remove(client)
                break
        return
    row['survey']['answers']['RND'] = uniformRND()
    answers = True if row['survey']['answers']['RND'] < 0.35 else False
    row['survey']['answers']['value'] = answers
    # Search for the client.
    # If the client answers, and queue is empty, the client will answer the survey
    # Else the client will wait or be deleted
    for client in row['clients']:
        if (client.status == 'SU'):
            if (answers):
                if (row['survey']['state'] == 'free'):
                    row['survey']['duration']['RND'] = uniformRND()
                    row['survey']['duration']['abs_time'] = logaritmicRND(
                        row['survey']['duration']['RND'], 10)
                    row['survey']['duration']['rel_time'] = truncate(
                        row['survey']['duration']['abs_time'] + row['clock'])
                    row['survey']['state'] = 'busy'
                    row['survey']['total_answered_surveys'] += 1
                else:
                    client.status = 'WA'
                    row['survey']['queue'] += 1
            else:
                row['clients'].remove(client)
                break


def survey_end_event(row):
    # Free the node
    row['survey']['state'] = 'free'
    row['survey']['duration']['RND'] = None
    row['survey']['duration']['abs_time'] = None
    row['survey']['duration']['rel_time'] = None
    # Search for the client who has been attended
    for client in row['clients']:
        if (client.status == 'SU'):
            row['clients'].remove(client)
            break
    # Check if there is a client in the queue
    if (row['survey']['queue'] > 0):
        # There is one client waiting
        row['survey']['queue'] -= 1
        row['survey']['state'] = 'busy'
        row['survey']['duration']['RND'] = uniformRND()
        row['survey']['duration']['abs_time'] = logaritmicRND(
            row['survey']['duration']['RND'], 10)
        row['survey']['duration']['rel_time'] = truncate(
            row['survey']['duration']['abs_time'] + row['clock'])
        row['survey']['total_answered_surveys'] += 1
        # Search for client who has waited the longest
        client = None
        for c in row['clients']:
            if (c.status == 'WA' and c.service == 'survey'):
                if (not client or client.arrival_time < c.arrival_time):
                    client = c
        client.survey(row['clock'])


def init_emptycols():
    row = {
        'N': 0,
        'event': 'start',
        'clock': 0,
        'starting_events': {},
        'ending_events': {},
        'service_states': {},
        'waiting_time': {},
        'total_queued_clients': {},
        'clients': []
    }
    for service in services:
        rnd = uniformRND()
        abs_time = logaritmicRND(rnd, service.arrival_freq)
        row['starting_events'][service.name] = {
            'rnd': rnd, 'abs_time': abs_time, 'rel_time': abs_time}
        row['ending_events'][service.name] = {
            'rnd': None, 'abs_time': None, 'services': {}}
        row['service_states'][service.name] = {}
        row['waiting_time'][service.name] = 0
        row['total_queued_clients'][service.name] = 0
        row['service_states'][service.name]['queue'] = 0
        for i in range(service.nodes):
            row['service_states'][service.name][i] = {
                'state': 'free', 'starting_time': None}
            row['ending_events'][service.name]['services'][i] = None
    return row


def simulate(n, save_from=-1):
    # -1 if we don't want to save
    if (save_from != -1):
        em = ExcelManager('TP4/simulation.xlsx')
    # Initialize the columns
    row = init_emptycols()
    if save_from != -1:
        export_row(row, em)
    # Initialize the simulation
    bar = ProgressBar(n, 40)
    for i in range(1, n+1):
        # Event handling
        event_handling(row)
        bar.display()
        # Save rows
        if (save_from != -1 and (save_from <= i <= save_from + amount_saved or i == n)):
            export_row(row, em)
    return row


def simulate_with_survey(n):
    # Initialize the columns
    row = init_emptycols()
    row['survey'] = {}
    row['survey']['answers'] = {}
    row['survey']['answers']['RND'] = None
    row['survey']['answers']['value'] = None
    row['survey']['duration'] = {}
    row['survey']['duration']['RND'] = None
    row['survey']['duration']['abs_time'] = None
    row['survey']['duration']['rel_time'] = None
    row['survey']['state'] = 'free'
    row['survey']['queue'] = 0
    row['survey']['total_answered_surveys'] = 0
    # Initialize the simulation
    bar = ProgressBar(n, 40)
    for i in range(1, n+1):
        # Event handling
        event_handling(row, manage_survey=True)
        bar.display()
    return row


def calculate_statistics(row):
    total_waited_time = sum(row['waiting_time'].values())
    total_queued_clients = sum(row['total_queued_clients'].values())
    average_waiting_time = total_waited_time / \
        total_queued_clients if total_queued_clients > 0 else 0
    # Get the slowest and fastest service
    slowest_service = max(row['waiting_time'], key=row['waiting_time'].get)
    fastest_service = min(row['waiting_time'], key=row['waiting_time'].get)
    print('1) Average waiting time:', round(
        average_waiting_time, 2), 'minutes')
    print('2) Slowest service:', slowest_service)
    print('4) Fastest service:', fastest_service)
    average_time_sl = row['waiting_time'][slowest_service] / \
        row['total_queued_clients'][slowest_service] if row['total_queued_clients'][slowest_service] > 0 else 0
    average_time_fs = row['waiting_time'][fastest_service] / \
        row['total_queued_clients'][fastest_service] if row['total_queued_clients'][fastest_service] > 0 else 0
    print('5) Average time in queue of the slowest service:',
          round(average_time_sl, 2), 'minutes')
    print('6) Average time in queue of the fastest service:',
          round(average_time_fs, 2), 'minutes')
    print('For the following requested stats, we need to run again the simulation')
    print('3) What would happen if one of the bookborrowing librarians is ill?')
    print('7) Add a new service: "Survey"')
    option = int(input('Continue? 0-No, 1-Yes: '))
    if (option == 0):
        return
    if (option == 1):
        services[0].nodes -= 1
        new_row = simulate_with_survey(row['N'])
        print('3) What would happen if one of the bookborrowing librarians is ill?')
        avg_waiting_time_bookborrowing = row['waiting_time']['bookborrowing'] / \
            new_row['total_queued_clients']['bookborrowing'] if new_row['total_queued_clients']['bookborrowing'] > 0 else 0
        new_avg_waiting_time = new_row['waiting_time']['bookborrowing'] / \
            new_row['total_queued_clients']['bookborrowing'] if new_row['total_queued_clients']['bookborrowing'] > 0 else 0
        relation_avg = new_avg_waiting_time / \
            avg_waiting_time_bookborrowing if new_avg_waiting_time > 0 else 0
        if (relation_avg > 1):
            print('The average waiting time for bookborrowing increased by', round(
                relation_avg, 2), 'times')
        else:
            print('The average waiting time for bookborrowing decreased by', round(
                relation_avg, 2), 'times')
        print('A total of', new_row['survey']
              ['total_answered_surveys'], 'surveys were answered.')


def export_row(row, em):
    em.add_row(row)


def menu():
    last_simulation = None
    while True:
        print('0. Exit')
        print('1. Simulate')
        print('2. Calculate statistics')
        print('3. Modify values')
        option = int(input('Select an option: '))
        if (option == 0):
            return
        if (option == 1):
            n = int(input('Enter the number of iterations: '))
            save_from = int(input('Enter the iteration to start saving: '))
            last_simulation = simulate(n, save_from)
        elif (option == 2):
            if (last_simulation == None):
                print('No simulation has been made')
                continue
            calculate_statistics(last_simulation)
        elif (option == 3):
            modify_menu()
        if (option not in range(0, 3)):
            print('Invalid option.')


if __name__ == '__main__':
    menu()
