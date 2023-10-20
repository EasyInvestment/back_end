import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

const LineChart = () => {
    const chartContainerRef = useRef(null);
    const [data, setData] = useState([]);
    const [chartInitialized, setChartInitialized] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/stockapp/monitor/')
            .then(response => {
                console.log('Server Response:', response);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Fetch error: ', error);
                setError(error.message);
            })
            .then(dataObj => {
                const actualData = dataObj.data || [];
                console.log("Actual array data:", actualData);

                const formattedData = actualData
                    .filter(item => item && typeof item.datetime === 'string' && typeof item.close === 'number')
                    .map(item => ({
                        time: item.datetime.split(' ')[0],
                        value: item.close
                    }));


                setData(formattedData);
            })
            .catch(error => {
                console.error('Fetch error: ', error);
            });
    }, []);

    useEffect(() => {
        if (chartContainerRef.current && data.length > 0 && !chartInitialized) {
            console.log('Initializing chart...');
            const chart = createChart(chartContainerRef.current, {
                width: 400,
                height: 300
            });
            const lineSeries = chart.addLineSeries();
            lineSeries.setData(data);
            setChartInitialized(true);
            console.log('Chart initialized and data set!');
        }
    }, [data, chartInitialized]);

    return (
        <div ref={chartContainerRef} style={{ width: '400px', height: '300px' }}>
        {data.length === 0 && !error && <p>Loading data...</p>}
        {error && <p>Error: {error}</p>}
    </div>
    );
};

export default LineChart;
