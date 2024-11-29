import React from "react";
import logo from "../assets/logo.png";
import "../index.css"
function Header() {
  return (
    <header className="fixed w-full bg-white top-0 h-40 flex items-center justify-between px-10">
      <div className="flex items-center space-x-4">
        <img src={logo} alt="logo" className="h-36 w-44" />
        <h1 className="text-6xl text-[#53CEFF] font-bold">RAILMILAP</h1>
      </div>
      <div className="flex space-x-8 text-[#53CEFF] text-2xl">
        {/* <p className="cursor-pointer">Login</p>
        <p className="cursor-pointer">Sign Up</p> */}
      </div>
    </header>
  );
}

export default Header;
