import React, { useState } from "react";
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import axios from "axios";
import { Navigate } from 'react-router-dom';

function SearchForm() {
  const [selectedDate, setSelectedDate] = useState(null);
  const [fromStation, setFromStation] = useState('');
  const [toStation, setToStation] = useState('');
  const [minWaitTime, setMinWaitTime] = useState(4);
  const [loading, setLoading] = useState(false);
  const [navigateData, setNavigateData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fromStation || !toStation || !selectedDate) {
      alert("Please fill in all fields before submitting!");
      return;
    }
    const day = selectedDate ? selectedDate.toLocaleString('en-US', { weekday: 'short' }) : null;
    const dataToSend = {
      fromStation: fromStation,
      toStation: toStation,
      journeyDate: selectedDate,
      day: day,
      minWaitTime: minWaitTime
    };

    try {
      setLoading(true);
      const response = await axios.post('http://127.0.0.1:8000/routes', dataToSend);
      setLoading(false);
      setNavigateData({
        results: response.data,
        details: { src: fromStation, des: toStation, day: day }
      });
    } catch (error) {
      setLoading(false);
      if (error.response && (error.response.status === 500 || error.response.status === 400)){
        alert(error.response.data['message']);
      } else {
        alert("Network Error");
      }
      console.error(error);
    }
  };

  if (navigateData) {
    return <Navigate to="/path" state={navigateData} />;
  }

  return (
    <div className="glass-card p-8 md:p-10 w-full max-w-xl mx-auto relative group">
      {/* Decorative top border */}
      <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-brand to-blue-600 rounded-t-3xl opacity-80"></div>
      
      <h2 className="text-3xl font-display font-bold text-slate-800 dark:text-white mb-8">Search Routes</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* From & To Stations Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">From Station</label>
            <input 
              className="w-full bg-slate-50 dark:bg-dark-bg border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all shadow-sm"
              placeholder="e.g. NDLS" 
              value={fromStation}
              onChange={(e) => setFromStation(e.target.value.toUpperCase())}
            />
          </div>

          <div className="flex flex-col space-y-2">
            <label className="text-sm font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">To Station</label>
            <input 
              className="w-full bg-slate-50 dark:bg-dark-bg border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all shadow-sm"
              placeholder="e.g. HWH" 
              value={toStation}
              onChange={(e) => setToStation(e.target.value.toUpperCase())}
            />
          </div>
        </div>

        {/* Date Row */}
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider flex justify-between">
            <span>Journey Date</span>
          </label>
          <DatePicker
            selected={selectedDate}
            onChange={(date) => setSelectedDate(date)}
            className="w-full bg-slate-50 dark:bg-dark-bg border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent transition-all shadow-sm"
            placeholderText="Select a date"
            dateFormat="dd/MM/yyyy"
            minDate={new Date()}
          />
        </div>

        {/* Slider Row */}
        <div className="flex flex-col space-y-4 pt-2">
          <div className="flex justify-between items-center">
            <label className="text-sm font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">Min Wait Time</label>
            <span className="font-display font-bold text-brand bg-brand/10 px-3 py-1 rounded-full text-sm">{minWaitTime} Hours</span>
          </div>
          <input 
            type="range" 
            min="1" 
            max="20" 
            value={minWaitTime} 
            onChange={(e) => setMinWaitTime(Number(e.target.value))} 
            className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand"
          />
          <div className="flex justify-between text-xs text-slate-400 font-medium">
            <span>1 hr</span>
            <span>20 hrs</span>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-6">
          <button 
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-brand to-blue-600 text-white font-bold px-6 py-4 text-lg hover:shadow-lg hover:shadow-brand/30 hover:-translate-y-0.5 transform transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="loader !border-[3px] !border-white/30 !border-l-white !w-5 !h-5"></div>
                <span>Searching...</span>
              </>
            ) : (
              <span>Find Connections</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default SearchForm;