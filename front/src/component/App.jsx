import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './header';
import Footer from './footer';
import Home from './home';
import Path from './routes'
function App() {

  return (
    <div>
    <Router>
      <Header/>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/path' element={<Path />} />
        </Routes>
        <Footer/>
    </Router>
    </div>
  );
}

export default App;
