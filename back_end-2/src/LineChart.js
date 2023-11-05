import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

const LineChart = () => {
    const chartContainerRef = useRef(null);
    const [data, setData] = useState([]);
    const [chartInitialized, setChartInitialized] = useState(false);
    const [error, setError] = useState(null);

    // Fetch data from the server
    useEffect(() => {
        fetch('http://127.0.0.1:8000/stockapp/monitor/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(dataObj => {
                const actualData = dataObj.data || [];
                console.log("Actual array data:", actualData);

                // Assuming there is no 'datetime' field in the data received
                const formattedData = actualData
                    .filter(item => item && typeof item.close === 'number')
                    .map((item, index) => ({
                        time: index, // Replace this with your logic to assign time stamps
                        value: item.close
                    }));

                setData(formattedData);
            })
            .catch(error => {
                console.error('Fetch error: ', error);
                setError(error.message);
            });
    }, []);

    // Initialize the chart
    useEffect(() => {
        if (chartContainerRef.current && data.length > 0 && !chartInitialized) {
            const chart = createChart(chartContainerRef.current, {
                width: chartContainerRef.current.clientWidth,
                height: chartContainerRef.current.clientHeight
            });
            const lineSeries = chart.addLineSeries();
            lineSeries.setData(data);
            setChartInitialized(true);
        }
    }, [data, chartInitialized]);

    return (
        <div ref={chartContainerRef} style={{ width: '100%', height: '300px' }}>
            {data.length === 0 && !error && <p>Loading data...</p>}
            {error && <p>Error: {error}</p>}
        </div>
    );
};

export default LineChart;
