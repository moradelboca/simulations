from values import *
import numpy as np
import pandas as pd
from pprint import pprint


class Client:
    def __init__(self, arrival_time, service):
        self.arrival_time = arrival_time
        self.status = 'WA'  # Waiting
        self.service = service
        self.node = None

    def __repr__(self):
        return f'Client: {self.service} - {self.status} - {self.node} - {self.arrival_time}'

    def attend(self, node):
        self.status = 'BA'  # Being attended
        self.node = node


def truncate(num, decimals=4):
    return int(num * (10**decimals)) / (10**decimals)


def logaritmicRND(rnd, freq):
    return truncate((-60/freq) * np.log(1 - rnd))


def uniformRND():
    return truncate(np.random.uniform(high=0.9999))


def search_next_event(row):
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
    return next_event


def event_handling(prev_row):
    next_event = search_next_event(prev_row)
    # Get the service frequencies
    service = None
    for s in services:
        if (s.name == next_event['name']):
            service = s
    row = prev_row
    row['event'] = next_event['type'] + ' ' + next_event['name']
    if (next_event['type'] == 'end'):
        row['event'] += ' ' + str(next_event['node'])
    row['clock'] = next_event['time']
    row['N'] += 1
    # Arrival event
    if (next_event['type'] == 'start'):
        # Generate next arival event
        row['starting_events'][next_event['name']]['rnd'] = uniformRND()
        row['starting_events'][next_event['name']
                               ]['abs_time'] = logaritmicRND(row['starting_events'][next_event['name']]['rnd'], service.arrival_freq)
        row['starting_events'][next_event['name']
                               ]['rel_time'] = truncate(row['starting_events'][next_event['name']]['abs_time'] + row['clock'])
        # Generate ending event
        row['ending_events'][next_event['name']]['rnd'] = uniformRND()
        row['ending_events'][next_event['name']]['abs_time'] = logaritmicRND(
            row['ending_events'][next_event['name']]['rnd'], service.service_freq)
        # Check if there is a free node
        free_node = None
        for i in range(service.nodes):
            if (row['service_states'][next_event['name']][i]['state'] == 'free'):
                free_node = i
                break
        # If there is a free node, assign the client to it
        if (free_node != None):
            row['service_states'][next_event['name']
                                  ][free_node]['state'] = 'busy'
            row['service_states'][next_event['name']
                                  ][free_node]['starting_time'] = row['clock']
            row['ending_events'][next_event['name']]['services'][free_node] = truncate(
                row['clock'] + row['ending_events'][next_event['name']]['abs_time'])
            client = Client(row['clock'], next_event['name'])
            client.attend(free_node)
            row['clients'].append(client)
        # If there is no free node, the client will wait
        else:
            row['service_states'][next_event['name']]['queue'] += 1
            row['clients'].append(Client(row['clock'], next_event['name']))
    # Ending event
    elif (next_event['type'] == 'end'):
        # Free the node
        row['service_states'][next_event['name']
                              ][next_event['node']]['state'] = 'free'
        row['service_states'][next_event['name']
                              ][next_event['node']]['starting_time'] = None
        row['ending_events'][next_event['name']
                             ]['services'][next_event['node']] = None
        # Remove the client who has been attended
        for client in row['clients']:
            if (client.status == 'BA' and client.service == next_event['name'] and client.node == next_event['node']):
                row['clients'].remove(client)
                break
        # Check if there is a client in the queue
        if (row['service_states'][next_event['name']]['queue'] > 0):
            # There is one client waiting
            row['service_states'][next_event['name']]['queue'] -= 1
            row['service_states'][next_event['name']
                                  ][next_event['node']]['state'] = 'busy'
            row['service_states'][next_event['name']
                                  ][next_event['node']]['starting_time'] = row['clock']
            # Generate new ending event
            row['ending_events'][next_event['name']]['rnd'] = uniformRND()
            row['ending_events'][next_event['name']]['abs_time'] = logaritmicRND(
                row['ending_events'][next_event['name']]['rnd'], service.service_freq)
            row['ending_events'][next_event['name']]['services'][next_event['node']] = truncate(
                row['clock'] + row['ending_events'][next_event['name']]['abs_time'])
            # Search for client who has waited the longest
            for client in row['clients']:
                if (client.status == 'WA' and client.service == next_event['name']):
                    client.attend(next_event['node'])
                    break
    return row


def simulate(n, save_from=0):
    # Initialize the columns
    prev_row = {
        'N': 0,
        'event': 'start',
        'clock': 0,
        'starting_events': {},
        'ending_events': {},
        'service_states': {},
        'clients': []
    }
    for service in services:
        rnd = uniformRND()
        abs_time = logaritmicRND(rnd, service.arrival_freq)
        prev_row['starting_events'][service.name] = {
            'rnd': rnd, 'abs_time': abs_time, 'rel_time': abs_time}
        prev_row['ending_events'][service.name] = {
            'rnd': None, 'abs_time': None, 'services': {}}
        prev_row['service_states'][service.name] = {}
        prev_row['service_states'][service.name]['queue'] = 0
        for i in range(service.nodes):
            prev_row['service_states'][service.name][i] = {
                'state': 'free', 'starting_time': None}
            prev_row['ending_events'][service.name]['services'][i] = None
    # Initialize the simulation
    for i in range(1, n):
        # Event handling
        row = event_handling(prev_row)
        # Save rows
        if (save_from <= i <= save_from + 10):
            export_table(row)


def export_table(df):
    pprint(df)


if __name__ == '__main__':
    export_table(simulate(10000000, 9999))
