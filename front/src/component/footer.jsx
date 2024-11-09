import React from 'react';
import "../index.css";

function Footer() {
  return (
    <div className="bg-black text-white w-full fixed bottom-0 left-0">
      <div className="flex justify-around items-center p-4">
        <a href="#" className="font-custom text-lg tracking-wide antialiased">About Us</a>
        <a href="#" className="font-custom text-lg tracking-wide antialiased">Contact Us</a>
      </div>
    </div>
  );
}

export default Footer;