import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

const LineChart = () => {
    const chartContainerRef = useRef(null);
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/stockapp/monitor/')
            .then(response => {
                console.log('Server Response:', response);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const formattedData = data.map(item => ({
                    time: item.date, 
                    value: item.close 
                }));
                setData(formattedData);
            })
            .catch(error => {
                console.error('Fetch error: ', error);
            });
    }, []);

    useEffect(() => {
        if (chartContainerRef.current && data.length > 0) {
            const chart = createChart(chartContainerRef.current, { 
                width: 400, 
                height: 300
            });
            const lineSeries = chart.addLineSeries();
            lineSeries.setData(data);
        }
    }, [data]);

    return <div ref={chartContainerRef}></div>;
};

export default LineChart;
