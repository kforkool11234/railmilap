import React, { useState, useEffect } from "react";
import io from "socket.io-client";

// Configure Socket.IO with proper options
const socket = io("127.0.0.1:5000", {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
});

function WaitlistResults({ src, des, day }) {
    const [waitlistResults, setWaitlistResults] = useState([]);
    const [loadingMore, setLoadingMore] = useState(true);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState(0);
    const [journeyDetails, setJourneyDetails] = useState({
        src: '',
        des: '',
        day: ''
    });

    useEffect(() => {
        // Connection status handling
        socket.on("connect", () => {
            console.log("Connected to server");
            setError(null);
        });

        socket.on("connect_error", (err) => {
            console.error("Connection error:", err);
            setError("Unable to connect to server. Please try again later.");
        });

        // Data events

        socket.on("new_journey", (newJourneys) => {
            setLoadingMore(true);
            setWaitlistResults((prevResults) => {
                const updatedResults = [...prevResults, ...newJourneys];
                return sortJourneys(updatedResults); // Sort as new results come in
            });
        });

        socket.on("details", (data) => {
            setJourneyDetails({
                src: data.src,
                des: data.des,
                day: data.day
            });
        });



        // Error handling
        socket.on("error", (data) => {
            setError(data.message);
            setLoadingMore(false);
        });

        socket.on("warning", (data) => {
            console.warn("Warning:", data.message);
        });

        socket.on("search_complete", (data) => {
            setWaitlistResults(sortJourneys(data.results));
            setLoadingMore(false);
        });

        socket.on("Done", () => {
            setLoadingMore(false);
            setProgress(100);
        });

        // Cleanup on unmount
        return () => {
            socket.off("connect");
            socket.off("connect_error");
            socket.off("deta");
            socket.off("details");
            socket.off("new_journey");
            socket.off("error");
            socket.off("warning");
            socket.off("search_complete");
            socket.off("Done");
        };
    }, []);

    // Helper function to convert "X:YY hrs" to total minutes
    const tt_min = (x) => {
        const [totalHours, totalMinutes] = x.split(':');
        const hours = parseInt(totalHours);
        const minutes = parseInt(totalMinutes.replace(' hrs', '').trim());
        return hours * 60 + minutes;
    };

    // Function to sort journeys based on total wait time
    const sortJourneys = (journeys) => {
        return [...journeys].sort((a, b) => tt_min(a.total) - tt_min(b.total));
    };

    return (
        <div className="container mx-auto p-4">
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            <h2 className="text-2xl font-bold text-center mb-6 text-blue-600">
                {journeyDetails.src && journeyDetails.des ? 
                    `Connecting Journeys from ${journeyDetails.src} to ${journeyDetails.des} on ${journeyDetails.day}` :
                    'Loading journey details...'
                }
            </h2>

            {/* Progress bar */}
            {loadingMore && (
                <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                    <div 
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>
            )}

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
                                    {loadingMore ? 'Fetching results, please wait...' : 'No results found'}
                                </td>
                            </tr>
                        ) : (
                            waitlistResults.map((journey, index) => (
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
                
                {loadingMore && progress < 100 && (
                    <div className="flex flex-col items-center justify-center py-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default WaitlistResults;