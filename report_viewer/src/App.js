import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import BenchmarkReport from './components/BenchmarkReport';
import ConversationReport from './components/ConversationReport'; 
import ModelHistoryReport from './components/ModelHistoryReport';

import './App.css';

function Home() {
  return (
    <div className="home-container">
      <h1 className="home-title">🦙 Green Llama Report Viewer</h1>
      <p className="home-subtitle">Choose a report type:</p>

      <div className="button-container">
        <Link to="/normal" className="home-button">🧪 Conversation Report</Link>
        <Link to="/benchmark" className="home-button">📊 Benchmark Report</Link>
        <Link to="/history" className="home-button">📚 Model History Report</Link>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/benchmark" element={<BenchmarkReport />} />
        <Route path="/normal" element={<ConversationReport />} />
        <Route path="/history" element={<ModelHistoryReport />} />
      </Routes>
    </Router>
  );
}

export default App;
