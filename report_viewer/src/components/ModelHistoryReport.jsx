import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import Papa from 'papaparse';
import 'react-tabs/style/react-tabs.css';
import './BenchmarkReport.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

const ModelHistoryReport = () => {
  const [dataByModel, setDataByModel] = useState({});

  useEffect(() => {
    const loadCSVs = async () => {
      try {
        const res = await fetch('/file-list.json');
        const allFiles = await res.json();
        const historyFiles = allFiles.filter(f =>
          f.startsWith('model_history/') && f.endsWith('_all_metrics.csv')
        );
  
        const allData = {};
  
        for (const filePath of historyFiles) {
          const file = filePath.replace('model_history/', '');
          const modelName = file.replace('_all_metrics.csv', '');
  
          const res = await fetch(`/${filePath}`);
          const text = await res.text();
  
          const parsed = Papa.parse(text.trim(), {
            header: true,
            skipEmptyLines: true,
          });
  
          const metrics = {};
          let cpu = 0, gpu = 0, ram = 0, co2 = 0;
  
          parsed.data.forEach(row => {
            const metric = row['Metric Name'];
            const prompt = row['Prompt']?.trim();
            const value = parseFloat(row['Value']);
            const time = parseFloat(row['Elapsed Time']);
  
            if (!metric || !prompt || isNaN(value) || isNaN(time)) return;
  
            if (!metrics[metric]) metrics[metric] = [];
            metrics[metric].push({ prompt, value, time });
  
            if (metric === 'CPU Energy (J)') cpu += value;
            if (metric === 'GPU Energy (J)') gpu += value;
            if (metric === 'RAM Energy (J)') ram += value;
            if (metric === 'Carbon Emissions (gCO2)') co2 += value;
          });
  
          Object.values(metrics).forEach(arr =>
            arr.forEach((d, i) => (d.index = i + 1))
          );
  
          allData[modelName] = {
            metrics,
            totals: { cpu, gpu, ram, co2 }
          };
        }
  
        setDataByModel(allData);
      } catch (err) {
        console.error('Failed to load model history files:', err);
      }
    };
  
    loadCSVs();
  }, []);

  const renderEnergyAndFacts = (totals) => {
    const pieData = [
      { name: 'CPU Energy (J)', value: totals.cpu },
      { name: 'GPU Energy (J)', value: totals.gpu },
      { name: 'RAM Energy (J)', value: totals.ram },
    ];

    const facts = [
      { icon: '📄', label: 'Sheets of A4 Paper', value: (totals.co2 / 4.7).toFixed(1) },
      { icon: '🚶', label: 'Km of Walking', value: (totals.co2 / 80).toFixed(2) },
      { icon: '📧', label: 'Emails Sent', value: Math.round(totals.co2 / 0.014).toLocaleString() },
      { icon: '🔍', label: 'Google Searches', value: Math.round(totals.co2 / 0.2).toLocaleString() },
    ];

    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', margin: '40px 0' }}>
        <div style={{ width: '50%' }}>
          <h3>Total Energy Distribution</h3>
          <PieChart width={1000} height={300}>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              dataKey="value"
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>
        <div style={{ width: '45%' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '20px' }}>🌍 Carbon Emissions Equivalent</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
            {facts.map((fact, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                padding: '12px 16px',
                backgroundColor: '#f0f4f8',
                borderRadius: '12px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
              }}>
                <div style={{ fontSize: '1.8rem', marginRight: '16px' }}>{fact.icon}</div>
                <div>
                  <div style={{ fontSize: '0.85rem', color: '#444' }}>{fact.label}</div>
                  <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>{fact.value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderGraphWithTable = (metricName, data, allMetrics) => {
    const total = data.reduce((sum, d) => sum + d.value, 0).toFixed(2);
    const totalTime = data.reduce((sum, d) => sum + d.time, 0).toFixed(2);

    const displayedMetrics = [
      'CPU Energy (J)', 'GPU Energy (J)', 'RAM Energy (J)',
      'Total Energy (J)', 'Carbon Emissions (gCO2)'
    ];

    const tableRows = data.map((entry) => {
      const row = {
        index: entry.index,
        prompt: entry.prompt,
      };

      displayedMetrics.forEach((metric) => {
        const match = allMetrics[metric]?.find(d => d.index === entry.index && d.prompt === entry.prompt);
        if (match) row[metric] = match.value.toFixed(2);
      });

      return row;
    });

    return (
      <div style={{ padding: '20px' }}>
        <p><strong>Total {metricName}:</strong> {total} over {totalTime} seconds</p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 80, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" label={{ value: 'Prompt Index', position: 'outsideBottom', offset: 10, dy: 20 }} />
            <YAxis label={{ value: metricName, angle: -90, position: 'insideLeft', dx: -20, dy: 70 }} />
            <Tooltip />
            <Legend verticalAlign="top" align="right" />
            <Line type="monotone" dataKey="value" stroke="#8884d8" name="Metric Value" />
          </LineChart>
        </ResponsiveContainer>

        <div style={{ marginTop: '30px' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '10px' }}>Prompt Summary</h3>
          <table className="report-table">
            <thead>
              <tr>
                <th>Prompt Index</th>
                <th>Prompt</th>
                {displayedMetrics.map((metric) => (
                  <th key={metric}>{metric}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, i) => (
                <tr key={i}>
                  <td>{row.index}</td>
                  <td>{row.prompt}</td>
                  {displayedMetrics.map((metric) => (
                    <td key={metric}>{row[metric] || '-'}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      <h1 className="title">📚 Model History Report</h1>
      <Tabs>
        <TabList>
          {Object.keys(dataByModel).map((modelName) => (
            <Tab key={modelName}>{modelName}</Tab>
          ))}
        </TabList>
        {Object.entries(dataByModel).map(([modelName, modelData]) => (
          <TabPanel key={modelName}>
            {renderEnergyAndFacts(modelData.totals)}
            <Tabs>
              <TabList>
                {Object.keys(modelData.metrics).map((metricName) => (
                  <Tab key={metricName}>{metricName}</Tab>
                ))}
              </TabList>
              {Object.entries(modelData.metrics).map(([metricName, data]) => (
                <TabPanel key={metricName}>
                  {renderGraphWithTable(metricName, data, modelData.metrics)}
                </TabPanel>
              ))}
            </Tabs>
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
};

export default ModelHistoryReport;
