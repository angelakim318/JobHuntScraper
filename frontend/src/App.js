import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';

const socket = io('http://127.0.0.1:5000');

function App() {
  const [jobs, setJobs] = useState([]);
  const [query, setQuery] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchJobs();

    // Listen for scrape progress messages
    socket.on('scrape_progress', (data) => {
      setMessage(data.message);
    });

    // Listen for scrape complete message
    socket.on('scrape_complete', () => {
      setMessage('Scraping completed. Fetching new job listings...');
      fetchJobs(); // Fetch the new job listings after scraping is complete
    });

    return () => {
      socket.off('scrape_progress');
      socket.off('scrape_complete');
    };
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/jobs');
      setJobs(response.data);
      setMessage(''); // Clear message after fetching jobs
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/jobs/search', {
        params: { query }
      });
      setJobs(response.data);
    } catch (error) {
      console.error('Error searching jobs:', error);
    }
  };

  const handleScrape = async () => {
    try {
      setMessage('Starting scraping...');
      await axios.post('http://127.0.0.1:5000/api/scrape');
    } catch (error) {
      console.error('Error scraping jobs:', error);
    }
  };

  return (
    <div className="App">
      <h1>Job Listings</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search job titles..."
      />
      <button onClick={handleSearch}>Search</button>
      <button onClick={handleScrape}>Scrape Jobs</button>
      {message && <p>{message}</p>}
      <ul>
        {jobs.map((job, index) => (
          <li key={index}>
            <h3>Job Title: {job.title}</h3>
            <p>Company: {job.company}</p>
            <p>Location: {job.location}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;