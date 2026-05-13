from django.db import models

class Station(models.Model):
    station_code = models.CharField(max_length=10, primary_key=True)
    station_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.station_name} ({self.station_code})"

class Train(models.Model):
    train_no = models.CharField(max_length=10, primary_key=True)
    train_name = models.CharField(max_length=100)
    source_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, related_name='source_trains')
    destination_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, related_name='destination_trains')

    def __str__(self):
        return f"{self.train_name} ({self.train_no})"

class TrainRunningDay(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='running_days')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)

    class Meta:
        unique_together = ('train', 'day_of_week')

    def __str__(self):
        return f"{self.train.train_no} - {self.day_of_week}"

class TrainSchedule(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='schedules')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='schedules')
    stop_sequence = models.IntegerField()
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    distance = models.IntegerField(default=0)
    day_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('train', 'stop_sequence')
        indexes = [
            models.Index(fields=['station']),
        ]

    def __str__(self):
        return f"{self.train.train_no} at {self.station.station_code} (Stop {self.stop_sequence})"
