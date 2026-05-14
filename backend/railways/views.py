from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import Station
from .scraper import get_train_running_days
from datetime import datetime, timedelta
import concurrent.futures

def time_to_seconds(day_str, time_obj, day_count=0):
    day_to_index = {
        "MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6
    }
    if day_str not in day_to_index:
        return 0
    day_index = day_to_index[day_str]
    total_seconds = ((day_index + day_count) * 24 * 60 * 60) + (time_obj.hour * 60 * 60) + (time_obj.minute * 60) + time_obj.second
    return total_seconds

def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(hours)}:{int(minutes):02d} hrs"

@api_view(['POST'])
def find_routes(request):
    data = request.data
    src = (data.get('fromStation') or '').upper()
    des = (data.get('toStation') or '').upper()
    day = (data.get('day') or '').upper()
    min_wait = data.get('minWaitTime', 4)
    
    try:
        min_wait = int(min_wait)
    except ValueError:
        min_wait = 4
    
    if not src or not des or not day:
        return Response({"message": "Please provide fromStation, toStation, and day"}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        Station.objects.get(station_code=src)
        Station.objects.get(station_code=des)
    except Station.DoesNotExist:
        return Response({"message": "Invalid station code"}, status=status.HTTP_400_BAD_REQUEST)

    # We will use raw SQL to find 1-interchange connections
    # T1 = first train, T2 = second train, S1 = src schedule, S2 = dest schedule
    # I1 = interchange schedule for T1, I2 = interchange schedule for T2
    
    query = """
    SELECT 
        T1.train_id AS FirstTrain,
        TR1.train_name AS FirstTrainName,
        T1.station_id AS InterchangeStation,
        ST.station_name AS InterchangeStationName,
        T1.arrival_time AS FirstTrainArrival,
        T1.day_count AS FirstTrainArrivalDayCount,
        T2.train_id AS SecondTrain,
        TR2.train_name AS SecondTrainName,
        T2.departure_time AS SecondTrainDeparture,
        T2.day_count AS SecondTrainDepartureDayCount,
        S1.departure_time AS FirstTrainSourceDeparture,
        S1.day_count AS FirstTrainSourceDayCount,
        S2.arrival_time AS SecondTrainDestArrival,
        S2.day_count AS SecondTrainDestDayCount
    FROM 
        railways_trainschedule T1
    JOIN 
        railways_trainschedule T2 
        ON T1.station_id = T2.station_id AND T1.train_id <> T2.train_id
    JOIN
        railways_trainschedule S1
        ON S1.train_id = T1.train_id AND S1.station_id = %s AND S1.stop_sequence < T1.stop_sequence
    JOIN
        railways_trainschedule S2
        ON S2.train_id = T2.train_id AND S2.station_id = %s AND S2.stop_sequence > T2.stop_sequence
    JOIN 
        railways_station ST ON ST.station_code = T1.station_id
    JOIN 
        railways_train TR1 ON TR1.train_no = T1.train_id
    JOIN 
        railways_train TR2 ON TR2.train_no = T2.train_id
    """
    
    results = []
    
    with connection.cursor() as cursor:
        cursor.execute(query, [src, des])
        rows = cursor.fetchall()
        
        # Process in python
        # Get unique trains to batch fetch running days
        unique_t1 = set(row[0] for row in rows)
        unique_t2 = set(row[6] for row in rows)
        all_unique_trains = list(unique_t1.union(unique_t2))
        
        # Cache running days concurrently to avoid slow sequential scraping
        train_running_days = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_train = {executor.submit(get_train_running_days, t): t for t in all_unique_trains}
            for future in concurrent.futures.as_completed(future_to_train):
                t = future_to_train[future]
                try:
                    train_running_days[t] = future.result()
                except Exception:
                    train_running_days[t] = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
            
        for row in rows:
            first_train = row[0]
            first_train_name = row[1]
            interchange = row[2]
            interchange_name = row[3]
            t1_arr_time = row[4]
            t1_arr_dc = row[5]
            second_train = row[6]
            second_train_name = row[7]
            t2_dep_time = row[8]
            t2_dep_dc = row[9]
            
            t1_src_dep_time = row[10]
            t1_src_dc = row[11]
            t2_dest_arr_time = row[12]
            t2_dest_dc = row[13]

            if not t1_arr_time or not t2_dep_time or not t1_src_dep_time or not t2_dest_arr_time: 
                continue
            
            # Check if FirstTrain runs on the correct origin day to reach the source on 'day'
            day_to_index = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}
            index_to_day = {0: "MON", 1: "TUE", 2: "WED", 3: "THU", 4: "FRI", 5: "SAT", 6: "SUN"}
            
            # If user boards on 'day', the train originated on 'day' minus 't1_src_dc'
            t1_origin_day_idx = (day_to_index[day] - t1_src_dc) % 7
            t1_origin_day = index_to_day[t1_origin_day_idx]
            
            runs_on_day = t1_origin_day in train_running_days[first_train] or 'Daily' in train_running_days[first_train]
            if not runs_on_day:
                continue
                
            # Wait time calculation
            # Since FirstTrain originates on 't1_origin_day', it arrives at Interchange on 't1_origin_day' + t1_arr_dc
            # Wait, since time_to_seconds uses absolute day, let's just compute absolute seconds since Monday
            t1_src_seconds = time_to_seconds(t1_origin_day, t1_src_dep_time, t1_src_dc)
            t1_arr_seconds = time_to_seconds(t1_origin_day, t1_arr_time, t1_arr_dc)
            t1_travel_seconds = (t1_arr_seconds - t1_src_seconds) % 604800
            
            # For SecondTrain, it could originate on any day. We check all its valid running days.
            t2_days = train_running_days[second_train]
            if 'Daily' in t2_days:
                t2_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                
            best_connection = None
            
            for t2_start_day in t2_days:
                # SecondTrain departs Interchange on t2_start_day + t2_dep_dc
                t2_dep_seconds = time_to_seconds(t2_start_day, t2_dep_time, t2_dep_dc)
                t2_dest_seconds = time_to_seconds(t2_start_day, t2_dest_arr_time, t2_dest_dc)
                t2_travel_seconds = (t2_dest_seconds - t2_dep_seconds) % 604800
                
                # Check wait time, handling week wrap-around modulo 7 days (604800 seconds)
                wait_seconds = (t2_dep_seconds - t1_arr_seconds) % 604800
                wait_hours = wait_seconds / 3600
                
                if min_wait <= wait_hours <= 24:
                    total_seconds = t1_travel_seconds + wait_seconds + t2_travel_seconds
                    if not best_connection or total_seconds < best_connection['total_seconds']:
                        best_connection = {
                            "station": f"{interchange_name} ({interchange})",
                            "train1": f"{first_train_name}",
                            "train2": f"{second_train_name}",
                            "interval": format_seconds(wait_seconds),
                            "total": format_seconds(total_seconds),
                            "wait_seconds": wait_seconds,
                            "total_seconds": total_seconds
                        }
            
            if best_connection:
                results.append(best_connection)

    # Sort by total journey time
    results.sort(key=lambda x: x['total_seconds'])
    
    return Response(results, status=status.HTTP_200_OK)
