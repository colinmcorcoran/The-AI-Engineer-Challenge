import React from 'react';
import { Analytics } from "@vercel/analytics/next"

const App: React.FC = () => {
  return (
    <div>
      <Analytics/>
      <h1>Welcome to The AI Engineer Challenge Frontend</h1>
    </div>
  );
};

export default App;
