import requests
import socket
from bs4 import BeautifulSoup
from django.db import transaction
from railways.models import Train, TrainRunningDay
import logging

logger = logging.getLogger(__name__)

def check_dns(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False

def get_running_days_from_web(train_no):
    """
    Scrapes etrain.info for the running days of a train and updates the database.
    """
    url = f"https://etrain.info/train/{train_no}/history"
    
    if not check_dns('etrain.info'):
        logger.error(f"DNS resolution failed for {url}")
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=(1, 3), allow_redirects=True)
        
        if response.status_code != 200:
            logger.error(f"Non-200 status code for {url}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.find("body")
        
        if not body:
            return None
        
        flex_col = body.find("div", class_="flexCol wd1012 pdlr2 pdu2")
        if not flex_col:
            return None
        
        lowerdata = flex_col.find(id="lowerdata")
        if not lowerdata:
            return None
            
        nocps_div = lowerdata.find("table", class_="nocps fullw bx3s trnd5")
        if not nocps_div:
            return None
            
        tbody = nocps_div.find("tr", class_="even dborder")
        
        if not tbody:
            return None
        
        inner_text = tbody.get_text(strip=True)
        days_list = inner_text.split(':')[1].split()
        
        if 'Daily' in days_list:
            days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        else:
            days = days_list
            
        # Save to database
        try:
            train = Train.objects.get(train_no=train_no)
            with transaction.atomic():
                # Clear existing to be safe
                TrainRunningDay.objects.filter(train=train).delete()
                
                day_objects = []
                for day in days:
                    if day in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
                        day_objects.append(TrainRunningDay(train=train, day_of_week=day))
                
                TrainRunningDay.objects.bulk_create(day_objects)
            return days
        except Train.DoesNotExist:
            logger.error(f"Train {train_no} does not exist in DB.")
            return None

    except Exception as e:
        logger.error(f"Error fetching days for {train_no}: {str(e)}")
        return None

def get_train_running_days(train_no):
    """
    Get running days from DB, if not found scrape them.
    """
    try:
        train = Train.objects.get(train_no=train_no)
    except Train.DoesNotExist:
        return []
        
    days = list(train.running_days.values_list('day_of_week', flat=True))
    if days:
        return days
    
    # Not in DB, scrape it
    days = get_running_days_from_web(train_no)
    # If scraping fails, default to daily so the app doesn't break
    return days or ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
