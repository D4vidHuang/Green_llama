import React, { useEffect, useState } from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const NormalReport = () => {
  const [groupedData, setGroupedData] = useState({});

  useEffect(() => {
    fetch('/metrics.csv')
      .then((res) => res.text())
      .then((csv) => {
        const lines = csv.trim().split('\n');
        const rawData = lines.map(line => {
          const [name, value, time] = line.split(',');
          return {
            name: name.trim(),
            value: parseFloat(value),
            time: parseFloat(time)
          };
        });

        const grouped = {};
        rawData.forEach(entry => {
          if (!grouped[entry.name]) grouped[entry.name] = [];
          grouped[entry.name].push(entry);
        });

        setGroupedData(grouped);
      });
  }, []);

  const renderGraph = (data, metricName) => {
    const totalValue = data.reduce((sum, d) => sum + d.value, 0).toFixed(2);
    const totalTime = data.reduce((sum, d) => sum + d.time, 0).toFixed(2);
    const showSummary = metricName.toLowerCase().includes("energy");

    return (
      <div style={{ padding: '20px' }}>
        {showSummary && (
          <p><strong>Total:</strong> {totalValue} kWh over {totalTime} seconds</p>
        )}
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" label={{ value: 'Elapsed Time (s)', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: metricName, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#82ca9d" name="Metric Value" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">🧪 Normal Usage Report</h1>
      <Tabs>
        <TabList>
          {Object.keys(groupedData).map((key, index) => (
            <Tab key={index}>{key}</Tab>
          ))}
        </TabList>

        {Object.entries(groupedData).map(([metricName, data], index) => (
          <TabPanel key={index}>
            {renderGraph(data, metricName)}
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
};

export default NormalReport;
