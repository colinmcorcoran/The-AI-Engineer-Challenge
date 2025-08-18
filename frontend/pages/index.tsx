import React, { useState } from 'react';

export default function Home() {
  const [developerMessage, setDeveloperMessage] = useState('');
  const [userMessage, setUserMessage] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4.1-mini');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const getApiUrl = () => {
    if (typeof window !== "undefined" && window.location.hostname === "localhost") {
      return "http://localhost:8000/api/chat";
    }
    return "/api/chat";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');
    try {
      const res = await fetch(getApiUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          developer_message: developerMessage,
          user_message: userMessage,
          model,
          api_key: apiKey
        })
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

      const reader = res.body?.getReader();
      let result = '';
      if (reader) {
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          result += decoder.decode(value);
          setResponse(result);
        }
      } else {
        setResponse(await res.text());
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
        <div>
          <label>Model:</label>
          <input
            type="text"
            value={model}
            onChange={e => setModel(e.target.value)}
          />
        </div>
        <div>
          <label>OpenAI API Key:</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
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