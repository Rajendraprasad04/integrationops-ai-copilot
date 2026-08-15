import React, { useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const EXAMPLE_QUESTIONS = [
  {
    question: "What is the normal integration pipeline?",
    type: "rag"
  },
  {
    question: "What happens during publishing?",
    type: "rag"
  },
  {
    question: "Why did JOB-1001 fail?",
    type: "tools"
  },
  {
    question: "How many records failed in JOB-1005?",
    type: "tools"
  },
  {
    question: "Why did JOB-1001 fail and what should normally happen during publishing?",
    type: "combined"
  }
];

function renderFormattedInline(str) {
  if (!str) return str;
  const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} style={{ color: '#FFF' }}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', padding: '0.15rem 0.4rem', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.875em' }}>
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

function renderFormattedAnswer(text) {
  if (!text) return null;
  const lines = text.split('\n');

  return lines.map((line, idx) => {
    if (line.startsWith('### ')) {
      return <h3 key={idx} style={{ color: '#38BDF8', marginTop: idx > 0 ? '1.25rem' : '0', marginBottom: '0.6rem', fontSize: '1.15rem', fontWeight: 700 }}>{line.replace('### ', '')}</h3>;
    }
    if (line.startsWith('#### ')) {
      return <h4 key={idx} style={{ color: '#A78BFA', marginTop: '0.85rem', marginBottom: '0.4rem', fontSize: '1.02rem', fontWeight: 600 }}>{line.replace('#### ', '')}</h4>;
    }
    if (line.startsWith('---')) {
      return <hr key={idx} style={{ borderColor: 'rgba(255,255,255,0.08)', margin: '1rem 0' }} />;
    }
    if (line.startsWith('- ')) {
      return (
        <div key={idx} style={{ marginLeft: '0.75rem', marginBottom: '0.4rem', display: 'flex', gap: '0.5rem', alignItems: 'baseline' }}>
          <span style={{ color: '#38BDF8' }}>•</span>
          <span>{renderFormattedInline(line.substring(2))}</span>
        </div>
      );
    }
    if (!line.trim()) {
      return <div key={idx} style={{ height: '0.3rem' }} />;
    }
    return <p key={idx} style={{ marginBottom: '0.5rem', lineHeight: 1.6 }}>{renderFormattedInline(line)}</p>;
  });
}

export default function App() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null);

  const handleAsk = async (queryText) => {
    const targetQuestion = queryText || question;
    if (!targetQuestion.trim()) return;

    setLoading(true);
    setError(null);
    setQuestion(targetQuestion);

    try {
      const res = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: targetQuestion }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("API Error:", err);
      setError(err.message || 'Failed to connect to backend server.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="container">
      {/* Header Section */}
      <header className="header">
        <h1>IntegrationOps AI Copilot</h1>
        <p className="subtitle">
          AI-powered integration troubleshooting and knowledge assistant
        </p>

        {/* Architecture Status Badges */}
        <div className="status-bar">
          <span className="status-badge active">
            <span className="status-dot"></span> RAG
          </span>
          <span className="status-badge active">
            <span className="status-dot"></span> Embeddings
          </span>
          <span className="status-badge active">
            <span className="status-dot"></span> Vector Search
          </span>
          <span className="status-badge active">
            <span className="status-dot"></span> Agent
          </span>
          <span className="status-badge active">
            <span className="status-dot"></span> Tools
          </span>
        </div>
      </header>

      {/* Example Questions Section */}
      <div className="section-title">Try Example Scenarios</div>
      <div className="examples-grid">
        {EXAMPLE_QUESTIONS.map((item, idx) => (
          <button
            key={idx}
            className={`example-card ${item.type === 'combined' ? 'combined-highlight' : ''}`}
            onClick={() => handleAsk(item.question)}
          >
            {item.question}
          </button>
        ))}
      </div>

      {/* Query Input Form */}
      <div className="query-box">
        <input
          type="text"
          className="query-input"
          placeholder="Ask a question (e.g. Why did JOB-1001 fail and what should normally happen?)"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="submit-btn"
          onClick={() => handleAsk()}
          disabled={loading || !question.trim()}
        >
          {loading ? 'Analyzing...' : 'Ask Copilot →'}
        </button>
      </div>

      {/* Error Message Display */}
      {error && (
        <div className="error-banner">
          ⚠️ <strong>Connection Error:</strong> {error} Make sure backend service is running at <code>{API_BASE_URL}</code>.
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analyzing intent, executing tools, and retrieving documentation...</p>
        </div>
      )}

      {/* Results Panel Display */}
      {response && !loading && (
        <div className="results-container">
          {/* Answer Card */}
          <div className="card">
            <div className="card-header">
              💡 Grounded Diagnostic Answer
            </div>
            <div className="answer-body">{renderFormattedAnswer(response.answer)}</div>
          </div>

          {/* Sources & Tools Two-Column Section */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {/* Sources Panel */}
            <div className="card">
              <div className="card-header">
                📚 Documentation Sources
              </div>
              <div className="badge-list">
                {response.sources && response.sources.length > 0 ? (
                  response.sources.map((src, i) => (
                    <span key={i} className="source-chip" title={src.section}>
                      📄 {src.document_name}
                      <small style={{ opacity: 0.75 }}>({src.section})</small>
                    </span>
                  ))
                ) : (
                  <span className="empty-chip">No documentation sources required for this query.</span>
                )}
              </div>
            </div>

            {/* Tools Used Panel */}
            <div className="card">
              <div className="card-header">
                🛠️ Operational Tools Invoked
              </div>
              <div className="badge-list">
                {response.tools_used && response.tools_used.length > 0 ? (
                  response.tools_used.map((tool, i) => (
                    <span key={i} className="tool-chip">
                      ⚡ {tool}
                    </span>
                  ))
                ) : (
                  <span className="empty-chip">No operational tools required for this query.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
