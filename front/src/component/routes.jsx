import React, { useState, useEffect } from "react";
import io from "socket.io-client";
import axios from "axios"
// Connect to the WebSocket server
const socket = io("127.0.0.1:5000/routes");

function WaitlistResults({ src, des, day }) {
    const [waitlistResults, setWaitlistResults] = useState([]);
    const [loadingMore, setLoadingMore] = useState(false);
    const [journeyDetails, setJourneyDetails] = useState({
        src: '',
        des: '',
        day: ''
    });

    useEffect(() => {
        // Listen for "new_journey" events from the server
        socket.on("new_journey", (newJourneys) => {
            setLoadingMore(true);
            setWaitlistResults((prevResults) => {
                // Update the results and turn off loading after this update
                const updatedResults = [...prevResults, ...newJourneys];
                return updatedResults;
            });
        });
        socket.on("details",(data)=>{
            setJourneyDetails({
                src:data.src,
                des:data.des,
                day:data.day
            })
            console.log(journeyDetails)
            if(data){
                console.log('true')
            }else{console.log('false')}
            // setJourneyDetails(details)
        })
        socket.on("Done", () => {
            setLoadingMore(false); // Stop loading when all data is received
        });

        // Clean up the event listener on component unmount
        return () => {
            socket.off("journey_details");
            socket.off("Done");
            socket.off("new_journey");
            
            
        };
    }, []);
    

    // Function to sort journeys based on total wait time
    const sortJourneys = (journeys) => {
        return journeys.sort((a, b) => {
            return tt_min(a.total) - tt_min(b.total); // Sort in ascending order
        });
    };

    // Helper function to convert "X:YY hrs" to total minutes
    const tt_min = (x) => {
        const [totalHours, totalMinutes] = x.split(':');
        const hours = parseInt(totalHours); // Convert hours part
        const minutes = parseInt(totalMinutes.replace(' hrs', '').trim()); // Convert minutes part
        return hours * 60 + minutes; // Total minutes
    };

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-2xl font-bold text-center mb-6 text-blue-600">
                {journeyDetails.src && journeyDetails.des ? 
                    `Connecting Journeys from ${journeyDetails.src} to ${journeyDetails.des} on ${journeyDetails.day}` :
                    'Loading journey details...'
                }
            </h2>
            <div className="overflow-x-auto rounded-lg shadow-lg">
                <table className="min-w-full bg-white border border-gray-200">
                    <thead>
                        <tr className="bg-blue-500 text-white">
                            <th className="py-3 px-4 border-b">Station</th>
                            <th className="py-3 px-4 border-b">Train 1</th>
                            <th className="py-3 px-4 border-b">Train 2</th>
                            <th className="py-3 px-4 border-b">Wait Time</th>
                            <th className="py-3 px-4 border-b">Total Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {waitlistResults.length === 0 ? (
                            <tr>
                                <td colSpan="5" className="text-center py-4">
                                    Fetching results, please wait...
                                </td>
                            </tr>
                        ) : (
                            sortJourneys(waitlistResults).map((journey, index) => (
                                <tr key={index} className="hover:bg-gray-100 transition duration-200">
                                    <td className="py-2 px-4 border-b">{journey.station}</td>
                                    <td className="py-2 px-4 border-b">{journey.train1}</td>
                                    <td className="py-2 px-4 border-b">{journey.train2}</td>
                                    <td className="py-2 px-4 border-b">{journey.interval}</td>
                                    <td className="py-2 px-4 border-b">{journey.total}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
                {loadingMore && (
                    <div className="flex justify-center items-center py-4">
                        <div className="loader"></div> {/* Loader component */}
                    </div>
                )}
            </div>
        </div>
    );
}

export default WaitlistResults;