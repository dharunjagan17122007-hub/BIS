import React, { useState } from "react";
import {
  Send,
  Bot,
  User,
  ShieldCheck,
  Search,
  FileText,
  ChevronRight,
  Loader2,
  AlertCircle,
  Sparkles,
  ExternalLink,
  Package,
  Building2,
} from "lucide-react";

import "./styles.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const exampleQueries = [
    "What is the standard for reinforced concrete?",
    "Which standard covers steel bars used for concrete?",
    "What are the requirements for steel reinforcement bars?",
    "How can I get BIS certification?",
  ];

  const sendQuery = async (text = query) => {
    const cleanQuery = text.trim();

    if (!cleanQuery || loading) {
      return;
    }

    setError("");
    setQuery("");

    const userMessage = {
      id: Date.now(),
      type: "user",
      text: cleanQuery,
    };

    setMessages((previous) => [...previous, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/chat/?query=${encodeURIComponent(cleanQuery)}`
      );

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        id: Date.now() + 1,
        type: "assistant",
        data,
      };

      setMessages((previous) => [...previous, assistantMessage]);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to BIS Navigator. Please make sure the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    sendQuery();
  };

  const renderSourceButton = (sourceUrl) => {
    if (!sourceUrl) {
      return null;
    }

    return (
      <a
        className="source-link"
        href={sourceUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        <ExternalLink size={16} />
        View Official BIS Source
      </a>
    );
  };

  const renderAssistantResponse = (data) => {
    if (!data) {
      return null;
    }

    // =====================================================
    // PRODUCT REQUIREMENTS
    // =====================================================

    if (data.response_type === "product_requirements") {
      return (
        <div className="response-content">
          <div className="response-heading">
            <Package size={20} />
            <span>Product Requirements</span>
          </div>

          {data.product && (
            <div className="primary-standard">
              <div className="standard-badge">
                <Package size={18} />
                Product Information
              </div>

              <h3>{data.product.product}</h3>

              <p className="standard-title">
                Applicable BIS Standard:{" "}
                <strong>{data.product.standard}</strong>
              </p>

              <div className="standard-meta">
                <span>
                  <strong>Category:</strong>{" "}
                  {data.product.category}
                </span>
              </div>

              <div className="description-section">
                <h4>Requirements</h4>

                <ul className="requirements-list">
                  {data.product.requirements?.map(
                    (requirement, index) => (
                      <li key={index}>{requirement}</li>
                    )
                  )}
                </ul>
              </div>

              {renderSourceButton(data.product.source_url)}
            </div>
          )}
        </div>
      );
    }

    // =====================================================
    // BIS SERVICE INFORMATION
    // =====================================================

    if (data.response_type === "service_information") {
      return (
        <div className="response-content">
          <div className="response-heading">
            <Building2 size={20} />
            <span>BIS Service</span>
          </div>

          {data.service && (
            <div className="primary-standard">
              <div className="standard-badge">
                <ShieldCheck size={18} />
                BIS Service
              </div>

              <h3>{data.service.name}</h3>

              <p className="standard-title">
                {data.service.description}
              </p>

              <div className="standard-meta">
                <span>
                  <strong>Category:</strong>{" "}
                  {data.service.category}
                </span>
              </div>
            </div>
          )}
        </div>
      );
    }

    // =====================================================
    // STANDARD RECOMMENDATION
    // =====================================================

    if (data.response_type === "recommendation") {
      return (
        <div className="response-content">
          <div className="response-heading">
            <Sparkles size={20} />
            <span>Recommended BIS Standard</span>
          </div>

          {data.best_match && (
            <div className="primary-standard">
              <div className="standard-badge">
                <ShieldCheck size={18} />
                Primary Match
              </div>

              <h3>{data.best_match.is_number}</h3>

              <p className="standard-title">
                {data.best_match.title}
              </p>

              <div className="standard-meta">
                <span>
                  <strong>Category:</strong>{" "}
                  {data.best_match.category}
                </span>

                <span>
                  <strong>Status:</strong>{" "}
                  {data.best_match.status}
                </span>
              </div>

              <div className="why-section">
                <h4>Why this standard?</h4>
                <p>{data.best_match.reason}</p>
              </div>

              {renderSourceButton(
                data.best_match.source_url
              )}
            </div>
          )}

          {data.related_standards?.length > 0 && (
            <div className="related-section">
              <div className="section-title">
                <FileText size={18} />
                <span>Related Standards</span>
              </div>

              <div className="related-list">
                {data.related_standards.map((standard) => (
                  <div
                    className="related-card"
                    key={standard.is_number}
                  >
                    <div>
                      <strong>{standard.is_number}</strong>
                      <p>{standard.title}</p>
                    </div>

                    <ChevronRight size={18} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    // =====================================================
    // DIRECT STANDARD LOOKUP
    // =====================================================

    if (data.response_type === "standard_lookup") {
      return (
        <div className="response-content">
          <div className="response-heading">
            <ShieldCheck size={20} />
            <span>BIS Standard</span>
          </div>

          <div className="primary-standard">
            <div className="standard-badge">
              <ShieldCheck size={18} />
              Standard Found
            </div>

            <h3>{data.standard?.is_number}</h3>

            <p className="standard-title">
              {data.standard?.title}
            </p>

            <div className="standard-meta">
              <span>
                <strong>Category:</strong>{" "}
                {data.standard?.category}
              </span>

              <span>
                <strong>Status:</strong>{" "}
                {data.standard?.status}
              </span>
            </div>

            {data.standard?.description && (
              <div className="description-section">
                <h4>Description</h4>
                <p>{data.standard.description}</p>
              </div>
            )}

            {renderSourceButton(
              data.standard?.source_url
            )}
          </div>
        </div>
      );
    }

    // =====================================================
    // CATEGORY SEARCH
    // =====================================================

    if (data.response_type === "category_search") {
      return (
        <div className="response-content">
          <div className="response-heading">
            <Search size={20} />
            <span>Standards Found</span>
          </div>

          {data.standards?.length > 0 ? (
            <div className="related-list">
              {data.standards.map((standard) => (
                <div
                  className="related-card"
                  key={standard.is_number}
                >
                  <div>
                    <strong>{standard.is_number}</strong>

                    <p>{standard.title}</p>

                    <small>
                      {standard.category} •{" "}
                      {standard.status}
                    </small>
                  </div>

                  <ChevronRight size={18} />
                </div>
              ))}
            </div>
          ) : (
            <p>No standards found for this category.</p>
          )}
        </div>
      );
    }

    // =====================================================
    // NO MATCH
    // =====================================================

    return (
      <div className="response-content">
        <div className="response-heading">
          <AlertCircle size={20} />
          <span>No Exact Match</span>
        </div>

        <p>
          {data.answer ||
            "I couldn't find a matching BIS standard. Try describing the product, material, or requirement in more detail."}
        </p>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h1>BIS Navigator</h1>
            <p>Indian Standards Assistant</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          BIS Assistant Online
        </div>
      </header>

      <main className="main-container">
        {messages.length === 0 ? (
          <section className="welcome">
            <div className="welcome-icon">
              <Bot size={42} />
            </div>

            <div className="welcome-text">
              <p className="eyebrow">
                AI-POWERED BIS ASSISTANT
              </p>

              <h2>
                Find the right
                <span> Indian Standard</span>
              </h2>

              <p className="welcome-description">
                Ask about BIS standards, product requirements,
                specifications, services, or manufacturing
                needs. BIS Navigator will identify the most
                relevant information for you.
              </p>
            </div>

            <div className="example-section">
              <h3>Try asking</h3>

              <div className="example-grid">
                {exampleQueries.map((example) => (
                  <button
                    key={example}
                    className="example-card"
                    onClick={() => sendQuery(example)}
                  >
                    <Search size={18} />
                    <span>{example}</span>
                    <ChevronRight size={17} />
                  </button>
                ))}
              </div>
            </div>
          </section>
        ) : (
          <section className="chat-section">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.type === "user"
                  ? "user-message"
                  : "assistant-message"
                  }`}
              >
                <div className="message-avatar">
                  {message.type === "user" ? (
                    <User size={18} />
                  ) : (
                    <Bot size={18} />
                  )}
                </div>

                <div className="message-body">
                  <div className="message-label">
                    {message.type === "user"
                      ? "You"
                      : "BIS Navigator"}
                  </div>

                  {message.type === "user" ? (
                    <div className="user-text">
                      {message.text}
                    </div>
                  ) : (
                    renderAssistantResponse(
                      message.data
                    )
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant-message">
                <div className="message-avatar">
                  <Bot size={18} />
                </div>

                <div className="message-body">
                  <div className="message-label">
                    BIS Navigator
                  </div>

                  <div className="loading-box">
                    <Loader2
                      className="spinner"
                      size={20}
                    />
                    <span>
                      Searching BIS information...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {error && (
          <div className="error-box">
            <AlertCircle size={19} />
            <span>{error}</span>
          </div>
        )}

        <form
          className="chat-input-wrapper"
          onSubmit={handleSubmit}
        >
          <div className="input-container">
            <Search size={21} />

            <input
              type="text"
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Ask about a BIS standard, product, service, or requirement..."
              disabled={loading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={!query.trim() || loading}
              aria-label="Send message"
            >
              {loading ? (
                <Loader2
                  className="spinner"
                  size={20}
                />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>

          <p className="input-hint">
            BIS Navigator provides source-backed information
            to help you identify relevant Indian Standards
            and BIS services.
          </p>
        </form>
      </main>
    </div>
  );
}

export default App;