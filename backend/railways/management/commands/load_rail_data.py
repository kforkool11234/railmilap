import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from railways.models import Station, Train, TrainSchedule
from django.db import transaction

class Command(BaseCommand):
    help = 'Load train schedule data from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        stations = {}
        trains = {}
        schedules = []

        self.stdout.write(self.style.SUCCESS('Parsing CSV and building objects in memory...'))

        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            
            # To keep track of day counts for each train
            train_day_tracker = {}

            for row in csv_reader:
                train_no = row['Train No.'].strip().strip("'")
                train_name = row['train Name'].strip()
                islno = int(row['islno'])
                station_code = row['station Code'].strip()
                station_name = row['Station Name'].strip()
                arrival_time_str = row['Arrival time'].strip().strip("'")
                departure_time_str = row['Departure time'].strip().strip("'")
                distance = int(row['Distance'].strip() or 0)
                source_code = row['Source Station Code'].strip()
                source_name = row['source Station Name'].strip()
                dest_code = row['Destination station Code'].strip()
                dest_name = row['Destination Station Name'].strip()

                # Add Stations
                if station_code not in stations:
                    stations[station_code] = Station(station_code=station_code, station_name=station_name)
                if source_code not in stations:
                    stations[source_code] = Station(station_code=source_code, station_name=source_name)
                if dest_code not in stations:
                    stations[dest_code] = Station(station_code=dest_code, station_name=dest_name)

                # Add Trains
                if train_no not in trains:
                    trains[train_no] = {
                        'train_name': train_name,
                        'source_code': source_code,
                        'dest_code': dest_code
                    }
                    train_day_tracker[train_no] = {
                        'previous_time': departure_time_str if departure_time_str != '00:00:00' and islno == 1 else '00:00:00',
                        'day_count': 0
                    }

                # Day Count Calculation
                tracker = train_day_tracker[train_no]
                prev_time_obj = datetime.strptime(tracker['previous_time'], "%H:%M:%S").time()
                curr_arr_time = datetime.strptime(arrival_time_str, "%H:%M:%S").time()
                curr_dep_time = datetime.strptime(departure_time_str, "%H:%M:%S").time()

                # Determine if we crossed midnight. We check against arrival if it's not the start, else departure.
                compare_time = curr_arr_time if arrival_time_str != '00:00:00' else curr_dep_time
                if compare_time < prev_time_obj and islno > 1:
                    tracker['day_count'] += 1

                # Use departure time for the next row's comparison, unless it's 00:00:00 (destination)
                next_compare = curr_dep_time if departure_time_str != '00:00:00' else curr_arr_time
                tracker['previous_time'] = next_compare.strftime("%H:%M:%S")

                schedule = TrainSchedule(
                    train_id=train_no,
                    station_id=station_code,
                    stop_sequence=islno,
                    arrival_time=curr_arr_time if arrival_time_str != '00:00:00' else None,
                    departure_time=curr_dep_time if departure_time_str != '00:00:00' else None,
                    distance=distance,
                    day_count=tracker['day_count']
                )
                schedules.append(schedule)

        self.stdout.write(self.style.SUCCESS(f'Saving {len(stations)} stations to database...'))
        with transaction.atomic():
            Station.objects.bulk_create(stations.values(), ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Saving {len(trains)} trains to database...'))
        train_objects = []
        for t_no, t_data in trains.items():
            train_objects.append(Train(
                train_no=t_no,
                train_name=t_data['train_name'],
                source_station_id=t_data['source_code'],
                destination_station_id=t_data['dest_code']
            ))
        with transaction.atomic():
            Train.objects.bulk_create(train_objects, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Saving {len(schedules)} schedules to database (this may take a minute)...'))
        with transaction.atomic():
            TrainSchedule.objects.bulk_create(schedules, batch_size=5000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Data load complete!'))
