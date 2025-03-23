import React, { useEffect, useState } from 'react';
import './BenchmarkReport.css'; // 👈 we’ll create this next

const BenchmarkReport = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/benchmark_log.json')
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => console.error("Failed to load JSON:", err));
  }, []);

  if (!data) return <div className="container">Loading...</div>;

  return (
    <div className="container">
      <h1 className="title">⚡ Benchmark Report</h1>
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
