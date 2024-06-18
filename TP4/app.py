from values import *
import numpy as np
import pandas as pd
import warnings
from pprint import pprint
warnings.simplefilter(action='ignore', category=FutureWarning)


start_events = ['bookborrowing', 'bookreturning',
                'consulting', 'computeruse', 'generalinfo']
end_events = [event+'_end' for event in start_events]
events = start_events + end_events


def initialize_vectors():
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
        rnd = round(np.random.uniform(high=0.9999), 4)
        abs_time = round((-60/service.arrival_freq) * np.log(1 - rnd), 4)
        prev_row['starting_events'][service.name] = {
            'rnd': rnd, 'abs_time': abs_time, 'rel_time': abs_time}
        prev_row['ending_events'][service.name] = {
            'rnd': rnd, 'abs_time': abs_time, 'services': {}}
        prev_row['service_states'][service.name] = {}
        for i in range(service.nodes):
            prev_row['service_states'][service.name][i] = {
                'state': 'free', 'starting_time': 0}
            prev_row['ending_events'][service.name]['services'][i] = 0

    return prev_row


def search_next_event(prev_row):
    next_event = None
    next_time = 0
    for event in events:
        if not next_event or prev_row[event, 'rel_time', ''] < next_time:
            next_event = event
            next_time = prev_row[event, 'rel_time', '']
    return next_event, next_time


def event_handling(event, time, prev_row):
    row = prev_row
    row['event', '', ''] = event
    row['N', '', ''] = prev_row['N', '', ''] + 1
    row['clock', '', ''] = time
    # Arrival event
    if (event in start_events):
        # Generate next aarival event
        row[event, 'rnd', ''] = round(np.random.uniform(high=0.9999), 4)
        row[event, 'abs_time', ''] = round((-60/request_freq[event]) *
                                           np.log(1 - prev_row[event, 'rnd', '']), 4)
        row[event, 'rel_time', ''] = row[event, 'abs_time', ''] + \
            prev_row['clock', '', '']
        # Generate ending event
        row[event+'_end', 'rnd', ''] = round(np.random.uniform(high=0.9999), 4)
        row[event+'_end', 'abs_time', ''] = round((-60/end_freq[event]) *
                                                  np.log(1 - prev_row[event+'_end', 'rnd', '']), 4)
        row[event+'_end', 'rel_time', ''] = row[event+'_end', 'abs_time', ''] + \
            prev_row['clock', '', '']

    return row


def simulate(n, save_from):
    prev_row = initialize_vectors()
    pprint(prev_row)
    # Initialize the simulation
    for i in range(1, n):
        # Get the next event
        event, time = search_next_event(prev_row)
        # Event handling
        row = event_handling(event, time, prev_row)
        # Save requested rows
        if (save_from <= i < save_from + 300):
            saved_rows.loc[len(saved_rows.index)] = row
    return saved_rows


def export_table(df):
    df.to_excel('./TP4/montecarloB.xlsx')


if __name__ == '__main__':
    export_table(simulate(10, 0))
