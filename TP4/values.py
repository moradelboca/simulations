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
            Service('computeruse', 8, 5, 1),
            Service('generalinfo', 25, 15, 2)]
