import openpyxl

EXCEL_PATH = './TP5/simulation.xlsx'


class SimulationPrinter():
    def __init__(self):
        self.eh = excelHandler

    def get_values(self, row, result=None):
        if result is None:
            result = []
        for key, value in row.items():
            if isinstance(value, dict):
                self.get_values(value, result)
            elif isinstance(value, list) and key == 'clients':
                for cli in value:
                    result.append(cli.__str__())
            else:
                result.append(value)
        return result

    def get_header(self, row, result=None, level=0):
        if result is None:
            result = [[]]
        # Flag to avoid phase shift when the level is changed
        first_value = True
        for key, value in row.items():
            for i in range(len(result)):
                if i == level:
                    result[i].append(key)
                else:
                    if i < level and not first_value:
                        result[i].append('')
            first_value = False
            if isinstance(value, dict):
                if level + 1 >= len(result):
                    result.append(['' for i in range(len(result[0]) - 1)])
                self.get_header(value, result, level + 1)
        return result

    def add_row(self, row):
        values = self.get_values(row)
        self.eh.add_sim_row(values)

    def add_header(self, row):
        header_rows = self.get_header(row)
        print(header_rows)
        for header_row in header_rows:
            self.eh.add_sim_row(header_row)


class ExcelHandler():
    def __init__(self, filename):
        self.filename = filename
        self.wb = openpyxl.Workbook()
        # Remove default sheet
        self.wb.remove(self.wb.active)
        self.wb.create_sheet(title='Simulation')
        self.wb.create_sheet(title='Runge Kutta')
        self.ws = self.wb['Simulation']

    def add_sim_row(self, row):
        if self.ws.title != 'Simulation':
            self.ws = self.wb['Simulation']
        self.ws.append(row)
        self.save()

    def add_rk_row(self, row):
        if self.ws.title != 'Runge Kutta':
            self.ws = self.wb['Runge Kutta']
        self.ws.append(row)
        self.save()

    def save(self):
        self.wb.save(self.filename)


excelHandler = ExcelHandler(EXCEL_PATH)
simulationPrinter = SimulationPrinter()

r1 = {'N': 1, 'event': 'start bookborrowing', 'clock': 1.0064, 'light_shutdown': {'start': {'RND': 0.0118, 'abs_time': 2.0, 'rel_time': 2.0, 'service': 'bookreturning'}, 'end': {'x_value': None, 'abs_time': None, 'rel_time': None}}, 'starting_events': {'bookborrowing': {'rnd': 0.9729, 'abs_time': 10.8246, 'rel_time': 11.831}, 'bookreturning': {'rnd': 0.8012, 'abs_time': 6.4618, 'rel_time': 6.4618}, 'consulting': {'rnd': 0.7493, 'abs_time': 8.3009, 'rel_time': 8.3009}, 'computeruse': {'rnd': 0.3471, 'abs_time': 3.1974, 'rel_time': 3.1974}, 'generalinfo': {'rnd': 0.5184, 'abs_time': 1.7535, 'rel_time': 1.7535}}, 'ending_events': {'bookborrowing': {'rnd': 0.3245, 'abs_time': 2.3538, 'services': {0: 3.3602, 1: None, 2: None}}, 'bookreturning': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None}}, 'consulting': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None}}, 'computeruse': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}}, 'generalinfo': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None}}},
      'service_states': {'bookborrowing': {'queue': 0, 0: {'state': 'busy', 'starting_time': 1.0064}, 1: {'state': 'free', 'starting_time': None}, 2: {'state': 'free', 'starting_time': None}}, 'bookreturning': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}}, 'consulting': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}}, 'computeruse': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}, 2: {'state': 'free', 'starting_time': None}, 3: {'state': 'free', 'starting_time': None}, 4: {'state': 'free', 'starting_time': None}, 5: {'state': 'free', 'starting_time': None}}, 'generalinfo': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}}}, 'waiting_time': {'bookborrowing': 0, 'bookreturning': 0, 'consulting': 0, 'computeruse': 0, 'generalinfo': 0}, 'total_queued_clients': {'bookborrowing': 0, 'bookreturning': 0, 'consulting': 0, 'computeruse': 0, 'generalinfo': 0}, 'clients': []}
r2 = {'N': 2, 'event': 'start generalinfo', 'clock': 1.7535, 'light_shutdown': {'start': {'RND': 0.0118, 'abs_time': 2.0, 'rel_time': 2.0, 'service': 'bookreturning'}, 'end': {'x_value': None, 'abs_time': None, 'rel_time': None}}, 'starting_events': {'bookborrowing': {'rnd': 0.9729, 'abs_time': 10.8246, 'rel_time': 11.831}, 'bookreturning': {'rnd': 0.8012, 'abs_time': 6.4618, 'rel_time': 6.4618}, 'consulting': {'rnd': 0.7493, 'abs_time': 8.3009, 'rel_time': 8.3009}, 'computeruse': {'rnd': 0.3471, 'abs_time': 3.1974, 'rel_time': 3.1974}, 'generalinfo': {'rnd': 0.4246, 'abs_time': 1.3264, 'rel_time': 3.0799}}, 'ending_events': {'bookborrowing': {'rnd': 0.3245, 'abs_time': 2.3538, 'services': {0: 3.3602, 1: None, 2: None}}, 'bookreturning': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None}}, 'consulting': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None}}, 'computeruse': {'rnd': None, 'abs_time': None, 'services': {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}}, 'generalinfo': {'rnd': 0.822, 'abs_time': 6.9038, 'services': {0: 8.6573, 1: None}}},
      'service_states': {'bookborrowing': {'queue': 0, 0: {'state': 'busy', 'starting_time': 1.0064}, 1: {'state': 'free', 'starting_time': None}, 2: {'state': 'free', 'starting_time': None}}, 'bookreturning': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}}, 'consulting': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}}, 'computeruse': {'queue': 0, 0: {'state': 'free', 'starting_time': None}, 1: {'state': 'free', 'starting_time': None}, 2: {'state': 'free', 'starting_time': None}, 3: {'state': 'free', 'starting_time': None}, 4: {'state': 'free', 'starting_time': None}, 5: {'state': 'free', 'starting_time': None}}, 'generalinfo': {'queue': 0, 0: {'state': 'busy', 'starting_time': 1.7535}, 1: {'state': 'free', 'starting_time': None}}}, 'waiting_time': {'bookborrowing': 0, 'bookreturning': 0, 'consulting': 0, 'computeruse': 0, 'generalinfo': 0}, 'total_queued_clients': {'bookborrowing': 0, 'bookreturning': 0, 'consulting': 0, 'computeruse': 0, 'generalinfo': 0}, 'clients': []}

if __name__ == '__main__':
    simulationPrinter.add_header(r1)
