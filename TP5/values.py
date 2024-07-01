class Service:
    def __init__(self, name, arrival_freq, service_freq, nodes):
        self.name = name
        # Number of students per hour requesting a service
        self.arrival_freq = arrival_freq
        # Number of students being attended per hour for each librarian
        self.service_freq = service_freq
        self.nodes = nodes  # Number of librarians or assistants attending the service


services = [Service('bookborrowing', 20, 10, 3),
            Service('bookreturning', 15, 12, 2),
            Service('consulting', 10, 8, 2),
            Service('computeruse', 8, 5, 6),
            Service('generalinfo', 25, 15, 2)]


amount_saved = 300
base_time = 0.5 # In seconds


# Menu to modify values and frequencies
def modify_menu():
    print('0. Exit')
    for i in range(len(services)):
        print(f'{i + 1}. {services[i].name}')
    option = int(input('Select a service to modify: '))
    if (option == 0):
        return
    if (option not in range(1, len(services) + 1)):
        print('Invalid option')
        return
    text = 'computers' if services[option -
                                   1].name == 'computeruse' else 'librarians'
    print('1. Modify arrival frequency (actual value: ' +
          str(services[option - 1].arrival_freq) + ')')
    print('2. Modify service frequency (actual value: ' +
          str(services[option - 1].service_freq) + ')')
    print('3. Modify amount of ' + text + ' (actual value: ' +
          str(services[option - 1].nodes) + ')')
    sub_option = int(input('Select an option: '))
    if (sub_option not in range(1, 4)):
        print('Invalid option')
        return
    if (sub_option == 1):
        services[option -
                 1].arrival_freq = int(input('Enter the new arrival frequency: '))
    elif (sub_option == 2):
        services[option -
                 1].service_freq = int(input('Enter the new service frequency: '))
    elif (sub_option == 3):
        services[option -
                 1].nodes = int(input('Enter the new amount of ' + text + ': '))
