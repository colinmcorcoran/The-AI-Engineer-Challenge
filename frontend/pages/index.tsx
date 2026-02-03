import React, { useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');
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

    if (message.trim() === '') {
      setResponse('Please enter a message.');
      setLoading(false);
      return;
    }


    try {
      const res = await fetch(getApiUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
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
          <label htmlFor="message">Message:</label>
          <textarea
            id="message"
            value={message}
            onChange={e => setMessage(e.target.value)}
            rows={8}
            style={{ width: '100%', whiteSpace: 'pre-wrap', resize: 'vertical' }}
            required
            wrap="soft"
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      <div>
        <h2>Response:</h2>
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', overflowWrap: 'break-word' }}>{response}</pre>
      </div>
    </div>
  );
}