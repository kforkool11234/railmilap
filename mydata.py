import csv
import pickle
from datetime import datetime, timedelta

def calculate_dd_hh_mm(previous_time_str, current_time_str, day_count):
    # Parse the time strings
    previous_time = datetime.strptime(previous_time_str, "%H:%M:%S")
    current_time = datetime.strptime(current_time_str, "%H:%M:%S")
    
    # Check for midnight crossing and increment day_count if necessary
    if current_time < previous_time:
        day_count += 1  # Increment day count due to midnight crossing
    
    # Add the day count to previous time
    new_time = current_time + timedelta(days=day_count)
    
    # Format new time in DD:HH:MM
    days = day_count
    hours = new_time.hour
    minutes = new_time.minute
    
    return f"{int(days)}:{int(hours):02}:{int(minutes):02}", day_count


def process_csv_to_json(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        trains_data = []
        
        for row in csv_reader:
            train_no = row['Train No.'].strip()
            train_name = row['train Name'].strip()
            station_code = row['station Code'].strip()
            departure_time = row['Departure time'].strip().strip("'")  # Use departure time and remove extra quotes if present
            distance = row["Distance"].strip()
            
            # Find or initialize the train entry
            train = next((t for t in trains_data if t["train_number"] == train_no), None)
            if not train:
                train = {
                    "train_name": train_name,
                    "train_number": train_no,
                    "stations": [],
                    "distances": [],
                    "previous_time":departure_time,
                    "day_count": 0
                }
                trains_data.append(train)
            
            # Calculate the DD:HH:MM time format for the current station
            previous_time = train["previous_time"]
            day_count = train["day_count"]
            departure_ddhhmm, updated_day_count = calculate_dd_hh_mm(previous_time, departure_time, day_count)
            # Append station and distance data
            train["stations"].append({station_code: departure_ddhhmm})
            train["distances"].append({station_code: distance})
            
            # Update the train's previous_time and day_count for the next station
            train["previous_time"] = departure_time
            train["day_count"] = updated_day_count
    
    # Save to JSON
    with open('restructuredData.pkl', mode='wb') as pkl_file:
        pickle.dump(trains_data, pkl_file)

# Usage
process_csv_to_json('isl_wise_train_detail_03082015_v1.csv')
