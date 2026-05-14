import React from 'react';

function Footer() {
  return (
    <div className="w-full bg-white/80 dark:bg-dark-bg/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 transition-colors duration-300 z-50">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center py-6 px-6 md:px-12 text-sm text-slate-500 dark:text-slate-400">
        <p>© 2026 RailMilap. All rights reserved.</p>
        <div className="flex space-x-6 mt-4 md:mt-0">
          <a href="/" className="hover:text-brand dark:hover:text-brand-light transition-colors font-medium">About Us</a>
          <a href="/" className="hover:text-brand dark:hover:text-brand-light transition-colors font-medium">Privacy</a>
          <a href="/" className="hover:text-brand dark:hover:text-brand-light transition-colors font-medium">Terms</a>
          <a href="/" className="hover:text-brand dark:hover:text-brand-light transition-colors font-medium">Contact Us</a>
        </div>
      </div>
    </div>
  );
}

export default Footer;