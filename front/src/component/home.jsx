import React from "react";
import SearchForm from "./search";

function Home() {
    return (
        <div className="min-h-[calc(100vh-100px)] pt-32 pb-24 px-6 md:px-12 lg:px-24 flex items-center justify-center relative overflow-hidden">
            {/* Background elements for rich aesthetics */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-brand/20 blur-[100px] animate-pulse"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-brand-dark/20 blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>

            <div className="w-full max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-16 z-10">
                
                {/* Text Content */}
                <div className="w-full lg:w-1/2 flex flex-col space-y-8 animate-fade-in-up">
                    <div className="inline-block px-4 py-1.5 rounded-full bg-brand/10 text-brand-dark dark:text-brand-light font-semibold text-sm w-max border border-brand/20">
                        ✨ India's Smartest Train Router
                    </div>
                    
                    <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-extrabold tracking-tight leading-tight text-slate-900 dark:text-white">
                        Find the perfect <br/>
                        <span className="text-gradient">Connection.</span>
                    </h1>
                    
                    <p className="text-lg md:text-xl text-slate-600 dark:text-slate-300 leading-relaxed max-w-xl">
                        Say goodbye to endless searching. We intelligently route you through the Indian Railways network to find the fastest, most convenient multi-train journeys available.
                    </p>

                    <div className="flex items-center space-x-6 pt-4">
                        <div className="flex flex-col">
                            <span className="text-3xl font-display font-bold text-slate-800 dark:text-white">500+</span>
                            <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">Stations</span>
                        </div>
                        <div className="w-px h-12 bg-slate-300 dark:bg-slate-700"></div>
                        <div className="flex flex-col">
                            <span className="text-3xl font-display font-bold text-slate-800 dark:text-white">3000+</span>
                            <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">Trains</span>
                        </div>
                    </div>
                </div>

                {/* Search Form */}
                <div className="w-full lg:w-1/2 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    <SearchForm/>
                </div>
            </div>
        </div>
    );
}

export default Home;