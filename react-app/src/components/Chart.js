import React, { useEffect, useState } from 'react';
import { Chart as ChartJS } from 'chart.js/auto';
import { Line } from 'react-chartjs-2';

ChartJS.defaults.color = "#FFFFFF"
ChartJS.defaults.borderColor = "#8F8F8F"

const LineChart = ({ time, pressure }) => {

  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: "tlak [hPa]",
        data: [],
        backgroundColor: "#7203FF",
        borderColor: "#7203FF",
        borderWidth: 5,
      }
    ]
  });

  let minPressure
  let maxPressure
  
  useEffect(() => {
    // Update chart data when time or pressure changes
    if (chartData.labels.length >= 180) {
      chartData.datasets.forEach(d => {
        d.data.shift();
      });
      chartData.labels.shift();
    }
  
    // Check if pressure is not equal to -1 before updating the chart data
    if (pressure !== -1) {
      setChartData(prevChartData => ({
        ...prevChartData,
        labels: [...prevChartData.labels, time],
        datasets: [
          {
            ...prevChartData.datasets[0],
            data: [...prevChartData.datasets[0].data, pressure]
          }
        ]
      }));
    }
  
    // Calculate min and max pressure only if pressure is not -1
    if (pressure !== -1 && pressure.length > 0) {
      minPressure = Math.min(...pressure);
      maxPressure = Math.max(...pressure);
    } else {
      // Set default values if pressure is -1 or empty
      minPressure = 0;
      maxPressure = 100;
    }
  
  }, [time, pressure]);


  

  const options = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        min: minPressure,
        max: maxPressure,
      }
    }
  }


    return (<Line data={chartData} options={options} height={270} width={800}/>);
};

export default LineChart;
