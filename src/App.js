// import logo from './logo.svg';
import './App.css';
import {   Route,  Routes, BrowserRouter } from 'react-router-dom';
import Signup from './components/Signup';

function App() {
  return (
    
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Signup/>}/>
        </Routes>
        
      </BrowserRouter>
   
  );
}

export default App;
