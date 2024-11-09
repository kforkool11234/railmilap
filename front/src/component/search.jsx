import React, { useState } from "react";
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import "../index.css";
import axios from "axios";
import { Navigate } from 'react-router-dom';

function SearchForm() {
  const [selectedDate, setSelectedDate] = useState(null);
  const [fromStation, setFromStation] = useState('');
  const [toStation, setToStation] = useState('');
  const [redirectToPath, setRedirectToPath] = useState(false); // State for redirection

  const handleSubmit = async (e) => {
    e.preventDefault();
    const day = selectedDate ? selectedDate.toLocaleString('en-US', { weekday: 'short' }) : null;
    const dataToSend = {
      fromStation: fromStation,
      toStation: toStation,
      journeyDate: selectedDate,
      day: day
    };

    try {
      const response = await axios.post('https://railmilap.onrender.com/routes', dataToSend);
      console.log(response.data);
      setRedirectToPath(true); // Set state to trigger navigation
    } catch (error) {
      if (error.status==500){
        alert(error.response.data['message'])
      }
      console.error(error.status);
    }
  };

  // Redirect if redirectToPath is true
  if (redirectToPath) {
    return <Navigate to="/path" />;
  }

  return (
    <div className="flex mt-10 justify-center">
      <div className="border-4 border-black rounded-3xl p-8 max-w-2xl">
        <h2 className="text-4xl text-[#53CEFF] mb-4">From</h2>
        <input 
          className="rounded-xl w-full max-w-xl mb-4 px-4 border border-black font-custom text-lg tracking-wide antialiased" 
          placeholder="Station code" 
          onChange={(e) => setFromStation(e.target.value)}
        />

        <h2 className="text-4xl text-[#53CEFF] mb-4">To</h2>
        <input 
          className="rounded-xl w-full max-w-xl mb-4 px-4 border border-black font-custom text-lg tracking-wide antialiased" 
          placeholder="Station code" 
          onChange={(e) => setToStation(e.target.value)}
        />

        <div>
          <h2 className="text-4xl text-[#53CEFF] mb-4">Journey Date</h2>
          <DatePicker
            selected={selectedDate}
            onChange={(date) => setSelectedDate(date)}
            className="rounded-xl w-full max-w-xl mb-6 px-4 border border-black font-custom text-lg tracking-wide antialiased"
            placeholderText="DD/MM/YY"
          />
        </div>

        <div className="flex justify-end">
          <button 
            className="rounded-xl bg-[#53CEFF] text-white font-bold px-6 py-3 text-lg hover:bg-blue-600 transition ease-in-out"
            type="submit"
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}

export default SearchForm;