import csv
import os
from django.core.management.base import BaseCommand
from railways.models import Station, Train, TrainSchedule
from datetime import datetime
from django.conf import settings

class Command(BaseCommand):
    help = 'Load train schedule from Trains schedule.csv'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        Train.objects.all().delete()
        Station.objects.all().delete()
        
        stations = {}
        trains_data = {}
        
        csv_path = os.path.join(settings.BASE_DIR.parent, 'Trains schedule.csv')
        self.stdout.write(f"Reading CSV from {csv_path}...")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                st_code = row['station_code'].strip().upper() if row.get('station_code') else ''
                st_name = row['station_name'].strip() if row.get('station_name') else ''
                t_no = str(row['train_number']).strip() if row.get('train_number') else ''
                t_name = row['train_name'].strip() if row.get('train_name') else ''
                
                if not st_code or not t_no:
                    continue
                    
                if st_code not in stations:
                    stations[st_code] = st_name
                    
                if t_no not in trains_data:
                    trains_data[t_no] = {
                        'name': t_name,
                        'stops': []
                    }
                
                arr = row.get('arrival', '').strip()
                dep = row.get('departure', '').strip()
                day_val = row.get('day', '')
                try:
                    day_count = int(float(day_val)) - 1 if day_val else 0
                except ValueError:
                    day_count = 0
                
                def parse_time(t_str):
                    if t_str and ':' in t_str:
                        # Sometimes seconds might be missing, but format seems to be HH:MM:SS
                        parts = t_str.split(':')
                        if len(parts) == 2:
                            t_str = f"{t_str}:00"
                        try:
                            return datetime.strptime(t_str, "%H:%M:%S").time()
                        except ValueError:
                            pass
                    return None
                    
                # The 'id' column might not exist or might be empty, we fallback to sequence of reading if so
                try:
                    stop_id = int(float(row.get('id', 0)))
                except ValueError:
                    stop_id = len(trains_data[t_no]['stops'])
                    
                trains_data[t_no]['stops'].append({
                    'station_code': st_code,
                    'arr': parse_time(arr),
                    'dep': parse_time(dep),
                    'day_count': day_count,
                    'id': stop_id
                })
        
        self.stdout.write("Creating Stations...")
        Station.objects.bulk_create([Station(station_code=c, station_name=n) for c, n in stations.items()], batch_size=1000)
        
        self.stdout.write("Creating Trains...")
        train_objects = []
        for t_no, t_data in trains_data.items():
            # Sort stops by id to determine the correct stop sequence
            t_data['stops'].sort(key=lambda x: x['id'])
            src_station_id = t_data['stops'][0]['station_code'] if t_data['stops'] else None
            dst_station_id = t_data['stops'][-1]['station_code'] if t_data['stops'] else None
            
            train_objects.append(Train(
                train_no=t_no,
                train_name=t_data['name'],
                source_station_id=src_station_id,
                destination_station_id=dst_station_id
            ))
            
        Train.objects.bulk_create(train_objects, batch_size=1000)
        
        self.stdout.write("Creating Schedules...")
        schedules = []
        for t_no, t_data in trains_data.items():
            for idx, stop in enumerate(t_data['stops']):
                schedules.append(TrainSchedule(
                    train_id=t_no,
                    station_id=stop['station_code'],
                    stop_sequence=idx + 1,
                    arrival_time=stop['arr'],
                    departure_time=stop['dep'],
                    distance=0,
                    day_count=stop['day_count']
                ))
        
        TrainSchedule.objects.bulk_create(schedules, batch_size=5000)
        
        self.stdout.write(self.style.SUCCESS("Successfully loaded new schedule data!"))
