-- ==========================================
-- RailMilap Database Initialization Script
-- ==========================================

-- Clean up existing tables before creation
DROP TABLE IF EXISTS TrainSchedules;
DROP TABLE IF EXISTS TrainRunningDays;
DROP TABLE IF EXISTS Trains;
DROP TABLE IF EXISTS Stations;

-- 1. Stations Table
-- Stores unique stations across the network
CREATE TABLE Stations (
    StationCode VARCHAR(10),
    StationName VARCHAR(100) NOT NULL,
    PRIMARY KEY (StationCode)
);

-- 2. Trains Table
-- Stores core information about a train.
CREATE TABLE Trains (
    TrainNo VARCHAR(10),
    TrainName VARCHAR(100) NOT NULL,
    SourceStationCode VARCHAR(10) REFERENCES Stations(StationCode),
    DestinationStationCode VARCHAR(10) REFERENCES Stations(StationCode),
    PRIMARY KEY (TrainNo)
);

-- 3. Train Running Days
-- Normalized representation replacing the local pickle cache
CREATE TABLE TrainRunningDays (
    TrainNo VARCHAR(10) REFERENCES Trains(TrainNo) ON DELETE CASCADE,
    DayOfWeek VARCHAR(3) CHECK (DayOfWeek IN ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')),
    PRIMARY KEY (TrainNo, DayOfWeek) 
);

-- 4. Train Schedules
-- Stores the stop-by-stop schedule for each train, utilizing DayCount to properly
-- sequence trips that last multi-day (midnight crossings).
CREATE TABLE TrainSchedules (
    TrainNo VARCHAR(10) NOT NULL,
    StationCode VARCHAR(10) NOT NULL,
    StopSequence INT NOT NULL,               -- Equivalent to islNo
    ArrivalTime TIME,
    DepartureTime TIME,
    Distance INT,                            -- Distance from Source
    DayCount INT DEFAULT 0,                  -- 0 for day 1, 1 for crossing midnight, etc.
    
    -- Naturally acts as a Clustered Index sorting rows sequentially for instant lookup
    PRIMARY KEY (TrainNo, StopSequence),    
    FOREIGN KEY (TrainNo) REFERENCES Trains(TrainNo) ON DELETE CASCADE,
    FOREIGN KEY (StationCode) REFERENCES Stations(StationCode) ON DELETE CASCADE
);

-- Non-clustered index on StationCode to rapidly identify all trains passing through a specific station
CREATE INDEX IDX_Schedule_Station ON TrainSchedules (StationCode);


-- ==========================================
-- Views & Demonstrative Queries
-- ==========================================

-- View: Station to Station distances and halts using window functions
CREATE VIEW vw_TrainSegmentAnalysis AS
SELECT 
    TrainNo,
    StationCode,
    StopSequence,
    Distance AS DistanceFromSource,
    -- Distance between current stop and PREVIOUS stop natively calculated
    Distance - COALESCE(LAG(Distance, 1) OVER (PARTITION BY TrainNo ORDER BY StopSequence), 0) AS SegmentDistance,
    ArrivalTime,
    DepartureTime
FROM 
    TrainSchedules;

-- =========================================================================
-- Routing Example Query Template
-- Finding connections involving exactly 1 interchange station 
-- where wait time is optimal.
-- Usage: Replace 'BBS' with your Source and 'BNC' with your Destination
-- =========================================================================
/*
SELECT 
    T1.TrainNo AS FirstTrain,
    T1.StationCode AS InterchangeStation,
    T1.ArrivalTime AS FirstTrainArrival,
    T2.TrainNo AS SecondTrain,
    T2.DepartureTime AS SecondTrainDeparture
FROM 
    TrainSchedules T1
JOIN 
    TrainSchedules T2 
    ON T1.StationCode = T2.StationCode
    AND T1.TrainNo <> T2.TrainNo
WHERE EXISTS (
    SELECT 1 FROM TrainSchedules S1 
    WHERE S1.TrainNo = T1.TrainNo 
      AND S1.StationCode = 'BBS' 
      AND S1.StopSequence < T1.StopSequence
)
AND EXISTS (
    SELECT 1 FROM TrainSchedules S2 
    WHERE S2.TrainNo = T2.TrainNo 
      AND S2.StationCode = 'BNC' 
      AND S2.StopSequence > T2.StopSequence
)
-- Order by arrival time into the interchange station
ORDER BY T1.ArrivalTime ASC;
*/
