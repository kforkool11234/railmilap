import eventlet
eventlet.monkey_patch()
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import urllib3
import json
import numpy as np
import pickle
import networkx as nx
from datetime import timedelta, datetime
import requests
from bs4 import BeautifulSoup
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, 
                   cors_allowed_origins=["http://localhost:3000", 'https://railmilap.vercel.app', "http://localhost:3000//path"],
                   async_mode='eventlet',
                   logger=True)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load data timing
start_time = time.time()
with open('station_code_to_index.json', 'r') as f:
    encode = json.load(f)
    decode = {index: code for code, index in encode.items()}
with open('available_train.pkl', 'rb') as f:
    avil = pickle.load(f)
with open('length.pkl', 'rb') as fi:
    length = pickle.load(fi)
with open('co_mat.pkl', 'rb') as f:
    co_mat = pickle.load(f)
with open('restructuredData.pkl', 'rb') as f:
    train_schedule = pickle.load(f)
with open('train_days_cache.pkl', 'rb') as f:
    train_days_cache = pickle.load(f)
print(f"Data loading time: {time.time() - start_time:.2f} seconds")

def emit_with_retry(event_name, data, retries=3):
    start_time = time.time()
    i=0
    for _ in range(retries):
        try:
            i+=1
            print(i)
            socketio.emit(event_name, data)
            print(f"Emit {event_name} time: {time.time() - start_time:.2f} seconds")
            return True
        except Exception as e:
           print('trying')
    return False

def res(src, des, day):
    total_start_time = time.time()
    try:
        results = get_waitlist_results(src, des, day)
        if results:
            emit_with_retry("search_complete", {"results": results})
        else:
            emit_with_retry("error", {"message": "No routes found"})
        print(f"Total response time: {time.time() - total_start_time:.2f} seconds")
        return "done"
    except Exception as e:
        emit_with_retry("error", {"message": str(e)})
        return "error"

def merge_nearby_nodes(center_node, graph, threshold=10):
    start_time = time.time()
    nearby_nodes = [
        node for node in list(graph.nodes())
        if node != center_node and length.get((center_node, node), float('inf')) < threshold
    ]
    for node in nearby_nodes:
        for successor in list(graph.successors(node)):
            for key, edge_data in graph.get_edge_data(node, successor).items():
                new_distance = length.get((center_node, node), 0) + length.get((node, successor), 0)
                graph.add_edge(center_node, successor, train=edge_data['train'], weight=new_distance)
        for predecessor in list(graph.predecessors(node)):
            for key, edge_data in graph.get_edge_data(predecessor, node).items():
                new_distance = length.get((predecessor, node), 0) + length.get((node, center_node), 0)
                graph.add_edge(predecessor, center_node, train=edge_data['train'], weight=new_distance)
        graph.remove_node(node)
    print(f"Merge nearby nodes time: {time.time() - start_time:.2f} seconds")
    return center_node

def save_cache(trd):
    with open('train_days_cache.pkl', 'wb') as f:
        pickle.dump(trd, f)
import socket
import requests
from functools import wraps
import signal

# Global timeout decorator
def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError("Function call timed out")
            
            # Set the signal handler and a timeout
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel the alarm
                return result
            except TimeoutError:
                print(f"Timeout for function call")
                return None
        return wrapper
    return decorator

@timeout(3)
def check_dns(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False

def get_running_days(url):
    start_time = time.time()
    
    # Pre-check DNS
    if not check_dns('etrain.info'):
        print(f"DNS resolution failed for {url}")
        return None
    
    try:
        response = requests.get(url, 
                                timeout=(2, 2),  # Connection and read timeout
                                allow_redirects=False)  # Prevent redirects
        
        # Quick early checks
        if response.status_code != 200:
            print(f"Non-200 status code for {url}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("body")
        
        if not body:
            print(f"No body found for {url}")
            return None
        
        flex_col = body.find("div", class_="flexCol wd1012 pdlr2 pdu2")
        
        if not flex_col:
            print(f"Invalid page structure for {url}")
            return None
        
        lowerdata = flex_col.find(id="lowerdata")
        nocps_div = lowerdata.find("table", class_="nocps fullw bx3s trnd5")
        tbody = nocps_div.find("tr", class_="even dborder")
        
        if not tbody:
            print("Could not find tbody.")
            return None
        
        inner_text = tbody.get_text(strip=True)
        days = inner_text.split(':')[1].split()
        
        print(f"Get running days time for {url}: {time.time() - start_time:.2f} seconds")
        return days
    
    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {str(e)}")
        return None
def convert_to_timedelta(time_str):
    days, hours, minutes = map(int, time_str.split(':'))
    return timedelta(days=days, hours=hours, minutes=minutes)
def get_time(train_schedule, train_number, station_code):
    for train in train_schedule:
        # Check if the train number matches
        if train["train_number"].strip("'") == train_number:
            # Loop through the stations to find the matching station code
            for station in train["stations"]:
                if station_code in station:
                    # Return time as timedelta, or as string if preferred
                    return (station[station_code])
    # If train or station is not found, return None
    return None
# Function to retrieve station time for a specific train and station
def get_station_time(train_schedule, train_number, station_code):
    for train in train_schedule:
        # Check if the train number matches
        if train["train_number"].strip("'") == train_number:
            # Loop through the stations to find the matching station code
            for station in train["stations"]:
                if station_code in station:
                    # Return time as timedelta, or as string if preferred
                    return convert_to_timedelta(station[station_code])
    # If train or station is not found, return None
    return None
def time_to_seconds(day, time):
    """Convert day and time to total seconds since Monday midnight."""
    day_to_index = {
        "MON": 0,
        "TUE": 1,
        "WED": 2,
        "THU": 3,
        "FRI": 4,
        "SAT": 5,
        "SUN": 6
    }
    
    days, hours, minutes = map(int, time.split(':'))
    day_index = day_to_index[day]
    
    # Total seconds calculation
    total_seconds = ((day_index + days) * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60)
    return total_seconds
def total_time(train1_time,train2_time,t1_num,t2_num,wait_time):
    t1=train1_time.split(':')
    t2=train2_time.split(':')
    w=wait_time.split(':')
    t1_min=int(int(t1[0])*24*60+int(t1[1])*60+int(t1[2]))
    t2_min=int(int(t2[0])*24*60+int(t2[1])*60+int(t2[2]))
    w_min=int(int(w[0])*60+int(w[1]))
    for train in train_schedule:
        if train["train_number"].strip("'") == t1_num:
            x=list(train['stations'][0].values())[0]
            x=x.split(':')
            x_min=int(int(x[0])*24*60+int(x[1])*60+int(x[2]))
                
        elif train["train_number"].strip("'") == t2_num:
            y=list(train['stations'][-1].values())[0]
            y=y.split(':')
            y_min=int(int(y[0])*24*60+int(y[1])*60+int(y[2]))
    
    tt=int((t1_min-x_min)+(y_min-t2_min)+w_min)
    t=f"{tt//60}:{tt%60} hrs"
    return (t)

def calculate_wait_time(train1_day, train1_time, train2_days, train2_time):
    # Get total seconds for Train 1
    train1_seconds = time_to_seconds(train1_day, train1_time)
    
    # Determine the next available arrival time for Train 2
    wait_times = []
    
    # Check if Train 2 runs daily
    is_train2_daily = 'Daily' in train2_days
    
    # If Train 2 is daily, we can consider it arriving every day
    if is_train2_daily:
        train2_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    
    for train2_day in train2_days:
        # Check if train2_day and train2_time are valid before processing
        if not train2_day or not train2_time:
            continue
        
        # Calculate seconds for Train 2 on the specific day
        try:
            train2_seconds = time_to_seconds(train2_day, train2_time)
        except KeyError as e:
            continue
        
        # Calculate waiting time only if Train 2 arrives after Train 1
        if train2_seconds > train1_seconds:
            wait_time_seconds = train2_seconds - train1_seconds
            
            # Convert wait time back to hours, minutes, and seconds
            hours_wait = wait_time_seconds // 3600
            minutes_wait = (wait_time_seconds % 3600) // 60
            seconds_wait = wait_time_seconds % 60
            
            wait_times.append((train2_day, hours_wait, minutes_wait, seconds_wait))
    
    return wait_times

def tt_min(x):
    hours, minutes = map(int, x.replace(" hrs","").split(':'))
    return(int(hours*60+minutes))



def get_waitlist_results(src, des, day):
    function_start_time = time.time()
    
    # Initial setup timing
    setup_start = time.time()
    emit_with_retry("details", {
        "src": src,
        "des": des,
        "day": day
    })
    
    src_co = encode[src]
    des_co = encode[des]
    print(f"Initial setup time: {time.time() - setup_start:.2f} seconds")

    # Graph construction timing
    graph_start = time.time()
    con_sta = []
    for i in co_mat:
        if i[0] == src_co:
            con_sta.append(i[1])
    
    intr = []
    for i in con_sta:
        if (i, des_co) in co_mat:
            intr.append(i)
    
    graph = nx.MultiDiGraph()
    graph.add_node(src_co)
    graph.add_node(des_co)
    
    for i in intr:
        graph.add_node(i)
    for i in intr:
        for j in avil.get((src_co, i), []):
            distance = length.get((src_co, i), 0.0)
            graph.add_edge(src_co, i, train=str(j), weight=distance)
        for j in avil.get((i, des_co), []):
            distance = length.get((i, des_co), 0.0)
            graph.add_edge(i, des_co, train=str(j), weight=distance)
    print(f"Graph construction time: {time.time() - graph_start:.2f} seconds")
    
    # Node merging timing
    merge_start = time.time()
    src_co = merge_nearby_nodes(src_co, graph)
    des_co = merge_nearby_nodes(des_co, graph)
    print(f"Node merging time: {time.time() - merge_start:.2f} seconds")
    
    waitlist_results = []
    sl = dict()
    
    # Station processing timing
    station_start = time.time()
    station_count = 0
    for i in list(graph.nodes()):
        if i == src_co or i == des_co:
            continue
        station_count += 1
        inner_start = time.time()
        
        in_edge = list(graph.in_edges(i, data=True))
        out_edge = list(graph.out_edges(i, data=True))
        
        for a in in_edge:
            in_t = get_station_time(train_schedule, a[2].get('train').strip("'"), decode[i])
            in_time_only = timedelta(hours=in_t.seconds // 3600, minutes=(in_t.seconds // 60) % 60)

            for b in out_edge:
                out_t = get_station_time(train_schedule, b[2].get('train').strip("'"), decode[i])
                out_time_only = timedelta(hours=out_t.seconds // 3600, minutes=(out_t.seconds // 60) % 60)
                dif = abs(in_time_only - out_time_only)

                if 4 < dif.total_seconds() / 3600 < 10:
                    if i not in sl:
                        sl[i] = []
                    sl[i].append({1: a[2].get('train').strip("'"), 2: b[2].get('train').strip("'")})
        
        print(f"Station {station_count} processing time: {time.time() - inner_start:.2f} seconds")
    
    print(f"Total station processing time: {time.time() - station_start:.2f} seconds")

    # Train schedule processing timing
    schedule_start = time.time()
    schedule_count = 0
    for i in sl:
        for entry in sl[i]:
            schedule_count += 1
            inner_start = time.time()
            try:
                train_id_1 = entry[1]
                train_id_2 = entry[2]

                # Get train days timing
                days_start = time.time()
                if train_id_1 in train_days_cache:
                    train1_days = train_days_cache[train_id_1]
                else:
                    url = f"https://etrain.info/train/{train_id_1}/history"
                    train1_days = get_running_days(url)
                    if train1_days is not None:  # Only cache if successful
                        train_days_cache[train_id_1] = train1_days
                    else:
                         train1_days = []
                print(f"Get train1 days time: {time.time() - days_start:.2f} seconds")
                
                if day in train1_days or 'Daily' in train1_days:
                    days_start = time.time()
                    if train_id_2 in train_days_cache:
                        train2_days = train_days_cache[train_id_2]
                    else:
                        url = f"https://etrain.info/train/{train_id_2}/history"
                        train2_days = get_running_days(url)
                        if train2_days is not None:  # Only cache if successful
                            train_days_cache[train_id_2] = train2_days
                        else:
                            train2_days = []
                    print(f"Get train2 days time: {time.time() - days_start:.2f} seconds")
                    
                    calc_start = time.time()
                    train1_day = day
                    train1_time = get_time(train_schedule, train_id_1, decode[i])
                    train2_day = train2_days
                    train2_time = get_time(train_schedule, train_id_2, decode[i])  
                    wait_times = calculate_wait_time(train1_day, train1_time, train2_day, train2_time)
                    print(f"Wait time calculation time: {time.time() - calc_start:.2f} seconds")
                    
                    for schedule in wait_times:
                        if schedule[1]>4 and schedule[1]<11:
                            journey_data = {
                                "station": decode[i],
                                "train1": train_id_1,
                                "train2": train_id_2,
                                "interval": f"{schedule[1]} hrs {schedule[2]} mins",
                                "total": total_time(train1_time, train2_time, train_id_1, train_id_2, f"{schedule[1]}:{schedule[2]}")
                            }
                            waitlist_results.append(journey_data)
                            emit_with_retry("new_journey", [journey_data])
                
            except Exception as e:
                if "Max retries exceeded with url" in str(e):
                    break
            print(f"Schedule {schedule_count} processing time: {time.time() - inner_start:.2f} seconds")
    
    print(f"Total schedule processing time: {time.time() - schedule_start:.2f} seconds")

    # Final processing timing
    final_start = time.time()
    waitlist_results = sorted(waitlist_results, key=lambda x: tt_min(x['total']))
    save_cache(train_days_cache)
    emit_with_retry("Done", None)
    print(f"Final processing time: {time.time() - final_start:.2f} seconds")
    
    print(f"Total function time: {time.time() - function_start_time:.2f} seconds")
    return waitlist_results

@app.route('/routes', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            data = request.json
            src = data['fromStation'].upper()
            des = data['toStation'].upper()
            day = data.get('day', '').upper()
            
            if not day:
                return jsonify({"message": "Please enter a date"}), 400
            
            if src not in encode or des not in encode or not src or not des:
                return jsonify({"message": "Invalid station code"}), 400
            
            # Start processing in background
            eventlet.spawn(res, src, des, day)
            return jsonify({"message": "Search started successfully"}), 202
            
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=False,
                use_reloader=False)