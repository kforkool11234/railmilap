import React, { useState } from "react";
import { useLocation, Navigate, useNavigate } from "react-router-dom";

const ROWS_PER_PAGE = 15;

function WaitlistResults() {
    const location = useLocation();
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    
    if (!location.state) {
        return <Navigate to="/" />;
    }

    const { results, details } = location.state;
    const waitlistResults = results || [];

    const totalPages = Math.max(1, Math.ceil(waitlistResults.length / ROWS_PER_PAGE));
    const startIdx = (currentPage - 1) * ROWS_PER_PAGE;
    const pageRows = waitlistResults.slice(startIdx, startIdx + ROWS_PER_PAGE);

    const goToPage = (page) => {
        setCurrentPage(Math.max(1, Math.min(page, totalPages)));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Generate page number buttons (show max 7, with ellipsis)
    const getPageNumbers = () => {
        const pages = [];
        if (totalPages <= 7) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            if (currentPage <= 4) {
                pages.push(1, 2, 3, 4, 5, '...', totalPages);
            } else if (currentPage >= totalPages - 3) {
                pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
            } else {
                pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
            }
        }
        return pages;
    };

    return (
        <div className="min-h-screen pt-32 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
            
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h2 className="text-3xl md:text-4xl font-display font-extrabold text-slate-900 dark:text-white tracking-tight">
                        Journey Results
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg">
                        {details.src} <span className="text-brand">→</span> {details.des} on <span className="font-semibold text-slate-700 dark:text-slate-300">{details.day}</span>
                        {waitlistResults.length > 0 && (
                            <span className="ml-3 text-sm bg-brand/10 text-brand-dark dark:text-brand font-semibold px-2.5 py-1 rounded-full">
                                {waitlistResults.length} connections
                            </span>
                        )}
                    </p>
                </div>
                
                <button 
                    onClick={() => navigate('/')}
                    className="px-5 py-2.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors flex items-center space-x-2"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    <span>Back</span>
                </button>
            </div>

            <div className="bg-white dark:bg-dark-card border border-slate-200 dark:border-dark-border rounded-3xl shadow-2xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
                                <th className="py-5 px-6 font-semibold text-sm uppercase tracking-wider text-slate-500 dark:text-slate-400">Interchange Station</th>
                                <th className="py-5 px-6 font-semibold text-sm uppercase tracking-wider text-slate-500 dark:text-slate-400">Train 1</th>
                                <th className="py-5 px-6 font-semibold text-sm uppercase tracking-wider text-slate-500 dark:text-slate-400">Train 2</th>
                                <th className="py-5 px-6 font-semibold text-sm uppercase tracking-wider text-slate-500 dark:text-slate-400">Wait Time</th>
                                <th className="py-5 px-6 font-semibold text-sm uppercase tracking-wider text-brand">Total Time</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                            {waitlistResults.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="py-16 text-center">
                                        <div className="flex flex-col items-center justify-center space-y-4">
                                            <div className="p-4 bg-slate-100 dark:bg-slate-800 rounded-full">
                                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                            </div>
                                            <p className="text-lg font-medium text-slate-600 dark:text-slate-400">No connections found</p>
                                            <p className="text-sm text-slate-500">Try adjusting your minimum wait time or selecting a different date.</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                pageRows.map((journey, index) => (
                                    <tr key={startIdx + index} className={index % 2 === 0 ? 'bg-white dark:bg-dark-card' : 'bg-slate-50 dark:bg-slate-800/40'}>
                                        <td className="py-4 px-6">
                                            <span className="font-semibold text-slate-800 dark:text-white">{journey.station.split('(')[0].trim()}</span>
                                            <span className="ml-2 text-xs font-mono bg-slate-100 dark:bg-slate-800 text-slate-500 px-2 py-1 rounded">({journey.station.split('(')[1]}</span>
                                        </td>
                                        <td className="py-4 px-6 text-slate-600 dark:text-slate-300">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-2 h-2 rounded-full bg-blue-400 flex-shrink-0"></div>
                                                <span>{journey.train1}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 text-slate-600 dark:text-slate-300">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0"></div>
                                                <span>{journey.train2}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 font-medium text-slate-500 dark:text-slate-400">
                                            {journey.interval}
                                        </td>
                                        <td className="py-4 px-6">
                                            <span className="inline-block bg-brand/10 text-brand-dark dark:text-brand font-bold px-3 py-1 rounded-full">
                                                {journey.total}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Footer */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                            Showing <span className="font-semibold text-slate-700 dark:text-slate-300">{startIdx + 1}–{Math.min(startIdx + ROWS_PER_PAGE, waitlistResults.length)}</span> of <span className="font-semibold text-slate-700 dark:text-slate-300">{waitlistResults.length}</span>
                        </p>

                        <div className="flex items-center space-x-1">
                            {/* Prev */}
                            <button
                                onClick={() => goToPage(currentPage - 1)}
                                disabled={currentPage === 1}
                                className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            </button>

                            {/* Page Numbers */}
                            {getPageNumbers().map((page, i) => (
                                page === '...' ? (
                                    <span key={`ellipsis-${i}`} className="px-3 py-1.5 text-slate-400">…</span>
                                ) : (
                                    <button
                                        key={page}
                                        onClick={() => goToPage(page)}
                                        className={`w-9 h-9 rounded-lg text-sm font-semibold ${
                                            currentPage === page
                                                ? 'bg-brand text-white shadow-sm'
                                                : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                                        }`}
                                    >
                                        {page}
                                    </button>
                                )
                            ))}

                            {/* Next */}
                            <button
                                onClick={() => goToPage(currentPage + 1)}
                                disabled={currentPage === totalPages}
                                className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default WaitlistResults;