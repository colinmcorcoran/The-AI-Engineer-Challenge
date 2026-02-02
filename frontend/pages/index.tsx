import React, { useState } from 'react';

export default function Home() {
  const [developerMessage, setDeveloperMessage] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const getApiUrl = () => {
    if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
      return "http://localhost:8000/api/chat";
    }
    return "/api/chat";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');

    const combinedMessage = `${developerMessage ? developerMessage + "\n\n" : ""}${userMessage}`.trim();

    try {
      const res = await fetch(getApiUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: combinedMessage })
      });

      if (!res.ok) {
        let errorMsg = 'Error: ' + res.statusText;
        try {
          const errorData = await res.json();
          if (errorData && errorData.detail) {
            errorMsg += `\n${errorData.detail}`;
          }
        } catch {
          // fallback if response is not JSON
          errorMsg += `\n${await res.text()}`;
        }
        setResponse(errorMsg);
        setLoading(false);
        return;
      }

      // Backend returns JSON { reply: "..." }
      const data = await res.json();
      if (data && data.reply) {
        setResponse(data.reply);
      } else {
        setResponse(JSON.stringify(data));
      }
    } catch (err: any) {
      setResponse('Network error: ' + err.message);
    }

    setLoading(false);
  };

  return (
    <div>
      <h1>Welcome to The AI Engineer Challenge Frontend</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Developer Message:</label>
          <input
            type="text"
            value={developerMessage}
            onChange={e => setDeveloperMessage(e.target.value)}
            required
          />
        </div>
        <div>
          <label>User Message:</label>
          <input
            type="text"
            value={userMessage}
            onChange={e => setUserMessage(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      <div>
        <h2>Response:</h2>
        <pre>{response}</pre>
      </div>
    </div>
  );
}