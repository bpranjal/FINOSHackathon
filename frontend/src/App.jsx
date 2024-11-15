import { useState,useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from "axios";
import Navbar from '../components/Navbar';

function App() {
  const [count, setCount] = useState(0);

  const fetchAPI = async () => {
    const response = await axios.get("http://127.0.0.1:8080/");
  };

  useEffect(() => {
    fetchAPI()
  }, [])

  return (
    <>
     <Navbar />
    </>
  )
}

export default App
