import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (selectedFile) {
      
      const validExtensions = ['.js', '.jsx', '.py'];
      const fileExtension = '.' + selectedFile.name.split('.').pop().toLowerCase();
      
      if (!validExtensions.includes(fileExtension)) {
        setError('Please upload a .js, .jsx, or .py file');
        setFile(null);
        setFileName('');
        return;
      }
      
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/analyze-code', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(`Failed to analyze code: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Clean Code Analyzer</h1>
        <p>Upload a React (.js/.jsx) or FastAPI (.py) file to analyze code quality</p>
      </header>
      
      <main className="App-main">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-container">
            <label className="file-input-label">
              {fileName || 'Choose a file...'}
              <input 
                type="file" 
                accept=".js,.jsx,.py" 
                onChange={handleFileChange} 
                className="file-input"
              />
            </label>
            <button 
              type="submit" 
              className="analyze-button"
              disabled={loading || !file}
            >
              {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>
          </div>
          
          {error && <div className="error-message">{error}</div>}
        </form>
        
        {result && (
          <div className="results-container">
            <h2>Analysis Results</h2>
            
            <div className="score-display">
              <div className="score-circle">
                <span className="score-value">{result.overall_score}</span>
                <span className="score-label">/100</span>
              </div>
            </div>
            
            <div className="breakdown-section">
              <h3>Score Breakdown</h3>
              <div className="score-categories">
                <ScoreCategory name="Naming Conventions" score={result.breakdown.naming} maxScore={10} />
                <ScoreCategory name="Function Length & Modularity" score={result.breakdown.modularity} maxScore={20} />
                <ScoreCategory name="Comments & Documentation" score={result.breakdown.comments} maxScore={20} />
                <ScoreCategory name="Formatting & Indentation" score={result.breakdown.formatting} maxScore={15} />
                <ScoreCategory name="Reusability & DRY" score={result.breakdown.reusability} maxScore={15} />
                <ScoreCategory name="Best Practices" score={result.breakdown.best_practices} maxScore={20} />
              </div>
            </div>
            
            <div className="recommendations-section">
              <h3>Recommendations</h3>
              <ul className="recommendations-list">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function ScoreCategory({ name, score, maxScore }) {
  const percentage = (score / maxScore) * 100;
  
  let barColor;
  if (percentage >= 80) barColor = '#4CAF50'; // Green
  else if (percentage >= 60) barColor = '#FFC107'; // Yellow
  else barColor = '#F44336'; // Red
  
  return (
    <div className="score-category">
      <div className="category-header">
        <span className="category-name">{name}</span>
        <span className="category-score">{score}/{maxScore}</span>
      </div>
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ 
            width: `${percentage}%`,
            backgroundColor: barColor
          }}
        />
      </div>
    </div>
  );
}

export default App;