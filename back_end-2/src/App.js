import React from 'react';
import './App.css';
import LineChart from './LineChart';
import backButton from './backbutton.png'; // 이미지 import

function App() {
    return (
        <div className="App">
            <a href="category.html">
                <img className="back" src={backButton} style={{ width: '90px', height: '40px' }} />
            </a>
            <hr />
            <h2>산업별 경제 사이클</h2>
            <LineChart />
        </div>
    );
}

export default App;
