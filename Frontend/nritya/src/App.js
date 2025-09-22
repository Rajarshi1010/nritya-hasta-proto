import Welcome from "./components/welcome";
import Dashboard from "./components/dashboard";

import { Routes, Route } from "react-router-dom";

import "./App.css"
import "./styles/welcome.css"
import "./styles/dashboard.css"

function App(){
  return (
    <div className="App">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
        <link href="https://fonts.googleapis.com/css2?family=Yatra+One&display=swap" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/css2?family=Alan+Sans:wght@300..900&display=swap" rel="stylesheet"/>  
      </head>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/dash" element={<Dashboard />} />
      </Routes>
    </div>
  )
}

export default App;
