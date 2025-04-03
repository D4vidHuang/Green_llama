import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import Papa from 'papaparse';
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import './BenchmarkReport.css'; // reuse styling

const FILE_PATH = 'conversation_metrics.csv';
const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

const ConversationReport = () => {
  const [metrics, setMetrics] = useState({});
  const [totals, setTotals] = useState(null);

  useEffect(() => {
    const loadCSV = async () => {
      try {
        const res = await fetch(`/${FILE_PATH}`);
        const text = await res.text();

        const parsed = Papa.parse(text.trim(), {
          header: true,
          skipEmptyLines: true,
        });

        const metricsByName = {};
        let cpu = 0, gpu = 0, ram = 0, co2 = 0;

        parsed.data.forEach(row => {
          const metricName = row['Metric Name'];
          const prompt = row['Prompt']?.trim();
          const value = parseFloat(row['Value']);
          const time = parseFloat(row['Elapsed Time']);

          if (!metricName || !prompt || isNaN(value) || isNaN(time)) return;

          if (!metricsByName[metricName]) metricsByName[metricName] = [];
          metricsByName[metricName].push({ prompt, value, time });

          if (metricName === 'CPU Energy (J)') cpu += value;
          if (metricName === 'GPU Energy (J)') gpu += value;
          if (metricName === 'RAM Energy (J)') ram += value;
          if (metricName === 'Carbon Emissions (gCO2)') co2 += value;
        });

        Object.values(metricsByName).forEach(arr =>
          arr.forEach((d, i) => (d.index = i + 1))
        );

        setMetrics(metricsByName);
        setTotals({ cpu, gpu, ram, co2 });
      } catch (err) {
        console.error('Error loading CSV:', err);
      }
    };

    loadCSV();
  }, []);

  const renderEnergyAndFacts = () => {
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

  const renderGraphWithTable = (metricName, data) => {
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
        const match = metrics[metric]?.find(d => d.index === entry.index && d.prompt === entry.prompt);
        if (match) row[metric] = match.value.toFixed(2);
      });

      return row;
    });

    return (
      <div style={{ padding: '20px' }}>
        <p><strong>Total {metricName}:</strong> {total} over {totalTime} seconds</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 80, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" label={{ value: 'Prompt Index', position: 'outsideBottom', offset: 10, dy: 20 }} />
            <YAxis label={{ value: metricName, angle: -90, position: 'insideLeft', dx: -20, dy: 70 }} />
            <Tooltip />
            <Legend verticalAlign="top" align="right" />
            <Bar dataKey="value" fill="#8884d8" name="Metric Value" />
          </BarChart>
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
      <h1 className="title">🗣️ Last Conversation Report</h1>
      {totals && renderEnergyAndFacts()}
      <Tabs>
        <TabList>
          {Object.keys(metrics).map((metric) => (
            <Tab key={metric}>{metric}</Tab>
          ))}
        </TabList>
        {Object.entries(metrics).map(([metric, data]) => (
          <TabPanel key={metric}>
            {renderGraphWithTable(metric, data)}
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
};

export default ConversationReport;