import React, { useState } from 'react';
import ReactDOM from 'react-dom';

function App() {
  const [message, setMessage] = useState('');

  const fetchMessage = () => {
    fetch('http://backend:8000/api/data')
      .then(response => response.json())
      .then(data => setMessage(data.message))
      .catch(error => setMessage('Failed to fetch data'));
  };

  return (
    <div>
      <h1>{message || 'Click the button to load data'}</h1>
      <button onClick={fetchMessage}>Fetch Data</button>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));