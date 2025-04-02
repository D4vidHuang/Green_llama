import React, { useEffect, useState } from 'react';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import Papa from 'papaparse';
import 'react-tabs/style/react-tabs.css';
import './BenchmarkReport.css';
import Plot from 'react-plotly.js';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];


const BenchmarkReport = () => {
  const [dataByModel, setDataByModel] = useState({});

  useEffect(() => {
    const loadBenchmarkCSVs = async () => {
      try {
        const res = await fetch('/file-list.json');
        const allFiles = await res.json();
  
        const benchmarkFiles = allFiles.filter((path) =>
          path.startsWith('benchmark_results/') && path.endsWith('.csv')
        );
  
        const allData = {};
  
        for (const filePath of benchmarkFiles) {
          const match = filePath.match(/benchmark_results\/(\w+)_benchmark\/(.*)_benchmark_log\.csv/);
          if (!match) continue;
  
          const benchmarkType = match[1]; // chat, code, text
          const modelName = match[2];     // gemma3_1b, llama3_2_1b, etc.
  
          const res = await fetch(`/${filePath}`);
          const text = await res.text();
          const parsed = Papa.parse(text, {
            header: true,
            skipEmptyLines: true,
          });
          
          const dataRows = parsed.data;
  
          const metricsByName = {};
          let cpu = 0, gpu = 0, ram = 0, co2 = 0;
  
          dataRows.forEach((row) => {
            const rawMetricName = row['Metric Name'];
            const rawPrompt = row['Prompt'];
            const valueStr = row['Value'];
            const timeStr = row['Elapsed Time'];

            if (!rawMetricName || !rawPrompt || !valueStr || !timeStr) return;
  
            const metricName = rawMetricName.trim();
            const prompt = rawPrompt.trim();
            const value = parseFloat(valueStr);
            const elapsedTime = parseFloat(timeStr);
  
            if (!metricsByName[metricName]) {
              metricsByName[metricName] = [];
            }
  
            metricsByName[metricName].push({
              prompt,
              value,
              time: elapsedTime,
            });
  
            if (metricName === 'CPU Energy (J)') cpu += value;
            if (metricName === 'GPU Energy (J)') gpu += value;
            if (metricName === 'RAM Energy (J)') ram += value;
            if (metricName === 'Carbon Emissions (gCO2)') co2 += value;
          });
  
          Object.entries(metricsByName).forEach(([metric, arr]) => {
            arr.forEach((item, i) => {
              item.index = i + 1;
            });
          });
  
          if (!allData[benchmarkType]) {
            allData[benchmarkType] = {};
          }
  
          allData[benchmarkType][modelName] = {
            metrics: metricsByName,
            totals: { cpu, gpu, ram, co2 },
          };
        }
  
        setDataByModel(allData); // allData = { chat: { model1: {} }, code: { model2: {} }, ... }
  
      } catch (err) {
        console.error('Failed to load benchmark CSVs:', err);
      }
    };
  
    loadBenchmarkCSVs();
  }, []);

  const renderGraphWithTable = (data, metricName, allMetrics) => {
    if (!data || data.length === 0) {
      return <div>No data for {metricName}</div>;
    }
  
    const totalValue = data.reduce((sum, d) => sum + d.value, 0).toFixed(2);
    const totalTime = data.reduce((sum, d) => sum + d.time, 0).toFixed(2);
  
    // Group values by unique prompt
    const promptMap = new Map();
    data.forEach(({ prompt, value }) => {
      const trimmed = prompt.trim();
      if (!promptMap.has(trimmed)) promptMap.set(trimmed, []);
      promptMap.get(trimmed).push(value);
    });
  
    const boxPlotTraces = [];
    let index = 1;
  
    for (const [prompt, values] of promptMap.entries()) {
      boxPlotTraces.push({
        y: values,
        x: Array(values.length).fill(`#${index}`), // Show #1, #2, etc. on x-axis
        type: 'box',
        name: `Prompt ${index}`,
        text: Array(values.length).fill(prompt),
        hovertemplate:
          `<b>Prompt ${index}</b><br><i>%{text}</i><br>Value: %{y}<extra></extra>`,
        boxpoints: 'all',
        jitter: 0.4,
        marker: { size: 4 },
      });
      index++;
    }
  
    const displayedMetrics = [
      'CPU Energy (J)',
      'GPU Energy (J)',
      'RAM Energy (J)',
      'Total Energy (J)',
      'Carbon Emissions (gCO2)',
    ];
  
    const tableRows = Array.from(promptMap.entries()).map(([prompt], i) => {
      const row = {
        index: i + 1,
        prompt,
      };
      displayedMetrics.forEach((metric) => {
        const matches = allMetrics[metric]?.filter(d => d.prompt === prompt);
        if (matches?.length) {
          const avg = matches.reduce((sum, d) => sum + d.value, 0) / matches.length;
          row[metric] = avg.toFixed(2);
        }
      });
      return row;
    });
  
    return (
      <div style={{ padding: '20px' }}>
        <p><strong>Total {metricName}:</strong> {totalValue} over {totalTime} seconds</p>
  
        {/* Box Plot */}
        <Plot
          data={boxPlotTraces}
          layout={{
            title: `${metricName} Distribution by Prompt Index`,
            xaxis: {
              title: 'Prompt Index',
              tickmode: 'array',
              tickvals: boxPlotTraces.map((_, i) => `#${i + 1}`),
              ticktext: boxPlotTraces.map((_, i) => `#${i + 1}`),
            },
            yaxis: { title: metricName },
            boxmode: 'group',
            margin: { t: 50, b: 100, l: 60, r: 30 },
          }}
          style={{ width: '100%', height: '400px' }}
        />
  
        {/* Table */}
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
        {/* Pie Chart */}
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
  
        {/* Carbon Facts — as stat cards */}
        <div style={{ width: '45%' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '20px' }}>🌍 Carbon Emissions Equivalent</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
            {facts.map((fact, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '12px 16px',
                  backgroundColor: '#f0f4f8',
                  borderRadius: '12px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                }}
              >
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

  return (
    <div className="container"> {/* 👈 your original CSS container */}
    <h1 className="title">📊 Benchmark Report</h1> {/* 👈 styled title from your CSS */}
      <Tabs>
        <TabList>
          {Object.keys(dataByModel).map((benchmarkType) => (
            <Tab key={benchmarkType}>{benchmarkType}</Tab>
          ))}
        </TabList>

        {Object.entries(dataByModel).map(([benchmarkType, models]) => (
          <TabPanel key={benchmarkType}>
            <Tabs>
              <TabList>
                {Object.keys(models).map((modelName) => (
                  <Tab key={modelName}>{modelName}</Tab>
                ))}
              </TabList>

              {Object.entries(models).map(([modelName, modelData]) => (
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
                        {renderGraphWithTable(data, metricName, modelData.metrics)}
                      </TabPanel>
                    ))}
                  </Tabs>
                </TabPanel>
              ))}
            </Tabs>
          </TabPanel>
        ))}
      </Tabs>
    </div>
  );
}
  

export default BenchmarkReport;
