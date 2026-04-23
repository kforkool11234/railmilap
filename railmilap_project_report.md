# RailMilap Project Report: Advanced Database & Routing Architecture

## 1. Problem Statement

In the context of the Indian Railways system, direct trains are not always available or optimally timed for passengers traveling between a specific Source and Destination. The core challenge of **RailMilap** is to identify efficient multi-leg journey options that securely connect travelers to their intended destination via an intersecting (layover) station. 

**Key Technical Challenges:**
1. **Wait Time Logic:** Connecting journeys are only viable if the layover time at the intersecting station is reasonable (specifically between 4 and 10 hours).
2. **Computational Overhead:** The previous architecture relied on storing enormous datasets within flat CSVs (`isl_wise_train_detail`) and transforming them into heavy in-memory data structures (`Pickle` caching and Python `networkx` graphs). This resulted in high initialization latency, enormous heap-memory footprint, and limited scalability when parsing complex network paths dynamically across days.
3. **Rollover Boundaries:** Train sequences that bridge over midnight inherently skew logic, requiring explicit day-count normalization to formulate wait-time accuracy.

## 2. How We Are Using SQL to Solve This

To transform the project into a highly scalable, enterprise-grade state, we are migrating the heavy computational routing logic to a **Relational Database Management System (RDBMS) via Advanced SQL**. 

**SQL Advantages over the Python In-Memory approach:**
- **Normalized Schema (Data Integrity):** Normalizing entities into `Stations`, `Trains`, and `TrainSchedules` avoids redundant string duplication, aggressively minimizing storage footprints.
- **Set Theory Graph Traversal:** Translating the `networkx` node merging and edges methodology natively into relational Set-Theory via **CTEs (Common Table Expressions) and SELF JOINs**. This offloads algorithmic routing complexity directly to the optimized database C-engine.
- **Window Functions for Computation:** SQL's Analytical Window Functions explicitly target the problem of dynamic variables, eradicating the need for custom Python `for` loops that attempt to calculate node distances locally.
- **Clustered Indexing (Speed):** Wrapping our schedule tracking around composite indexes intrinsically sorts data down at the hardware physical-disk level, allowing the database to produce specific train histories instantly.

---

## 3. Important Code Portions

The following highlights the vital SQL implementation replacing the local application logic inside the backend.

### A. The Master Routing Algorithm (Graph Traversal Equivalent)
This piece is the heart of the system. It replaces the complex graph construction found in `app.py`. By utilizing a `SELF JOIN`, it automatically flags single-stop interchange stations, enforces the 4-to-10 hour layover rule implicitly, and uses `EXISTS` subqueries to guarantee route ordering matching the `source -> interchange -> destination` path.

```sql
DECLARE @SourceStation VARCHAR(10) = 'BBS';
DECLARE @TargetStation VARCHAR(10) = 'BNC';

SELECT 
    T1.TrainNo AS FirstTrain,
    T1.StationCode AS InterchangeStation,
    T1.ArrivalTime AS FirstTrainArrival,
    T2.TrainNo AS SecondTrain,
    T2.DepartureTime AS SecondTrainDeparture,
    DATEDIFF(HOUR, T1.ArrivalTime, T2.DepartureTime) AS LayoverHours
FROM 
    TrainSchedules T1
JOIN 
    TrainSchedules T2 
    ON T1.StationCode = T2.StationCode  -- Discovers the Intersecting Station
    AND T1.TrainNo <> T2.TrainNo        -- Enforces Train Transfer
WHERE EXISTS (
    SELECT 1 FROM TrainSchedules S1 
    WHERE S1.TrainNo = T1.TrainNo 
      AND S1.StationCode = @SourceStation 
      AND S1.StopSequence < T1.StopSequence -- First segment moves FORWARD
)
AND EXISTS (
    SELECT 1 FROM TrainSchedules S2 
    WHERE S2.TrainNo = T2.TrainNo 
      AND S2.StationCode = @TargetStation 
      AND S2.StopSequence > T2.StopSequence -- Second segment moves FORWARD
)
-- Implements the Wait Time Rule (4 to 10 hours limit)
AND DATEDIFF(HOUR, T1.ArrivalTime, T2.DepartureTime) BETWEEN 4 AND 10
ORDER BY LayoverHours ASC;
```

### B. Analytical Processing (Replacing Python Loops)
This demonstrates high-level statistical SQL capabilities by rendering sequence distance aggregates without ever pulling the core dataset into standard application memory.

```sql
SELECT 
    TrainNo,
    StationCode,
    StopSequence,
    -- Uses the LAG function to identify the data of the previous row 
    -- inherently creating distance segmentation dynamically.
    Distance - LAG(Distance, 1, 0) OVER (
        PARTITION BY TrainNo ORDER BY StopSequence
    ) AS StationToStationDistance,
    
    DATEDIFF(MINUTE, ArrivalTime, DepartureTime) AS HaltTimeMinutes
FROM 
    TrainSchedules
WHERE 
    TrainNo = '00851';
```

### C. Normalization & Integrity Enforcement
By binding our database structure using the `ON DELETE CASCADE` instruction, we ensure that if a Train is removed from the network via an administrative view, all related operational schedules are inherently removed, leaving zero orphaned metadata.

```sql
CREATE TABLE TrainSchedules (
    TrainNo VARCHAR(10) NOT NULL,
    StationCode VARCHAR(10) NOT NULL,
    StopSequence INT NOT NULL,              
    ArrivalTime TIME,
    DepartureTime TIME,
    Distance INT,                           
    DayCount INT DEFAULT 0,                 
    
    -- Hardware-level clustered index for instantaneous sequential reading
    PRIMARY KEY (TrainNo, StopSequence),    
    FOREIGN KEY (TrainNo) REFERENCES Trains(TrainNo) ON DELETE CASCADE,
    FOREIGN KEY (StationCode) REFERENCES Stations(StationCode) ON DELETE CASCADE
);
```
