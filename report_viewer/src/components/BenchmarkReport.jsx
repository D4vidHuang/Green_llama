import React, { useEffect, useState } from 'react';
import './BenchmarkReport.css';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const BenchmarkReport = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/benchmark_log.json')
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => console.error("Failed to load JSON:", err));
  }, []);

  if (!data) return <div className="container">Loading...</div>;

  const chartData = data.values.map((value, i) => ({ index: i + 1, value }));

  return (
    <div className="container">
      <h1 className="title">⚡ Benchmark Report</h1>

      <div style={{ width: '100%', height: 300, marginBottom: '40px' }}>
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" label={{ value: 'Prompt Index', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'CPU Usage (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#82ca9d"
              dot={true}
              
              name="CPU Usage"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <table className="report-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Prompt</th>
            <th>CPU Usage (%)</th>
            <th>Time (s)</th>
          </tr>
        </thead>
        <tbody>
          {data.prompts.map((prompt, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>{prompt}</td>
              <td>{data.values[i]?.toFixed(2)}</td>
              <td>{data.times[i]?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BenchmarkReport;
