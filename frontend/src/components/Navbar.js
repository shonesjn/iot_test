import React from 'react';
import saintgitsLogo from '../assets/images.png'; // adjust path as needed

const Navbar = ({ onToggleSidebar }) => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <button className="hamburger-btn" onClick={onToggleSidebar}>
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
        </button>
        
        <div className="logo">
          <img src={saintgitsLogo} alt="Saintgits Logo" className="logo-img" />
        </div>
      </div>
      
      <div className="navbar-center">
        <h1 className="navbar-title">IOT Dashboard</h1>
      </div>

    </nav>
  );
};

export default Navbar;

