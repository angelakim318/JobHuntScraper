import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import JobList from './components/JobList';
import SearchBar from './components/SearchBar';
import ScrapeButton from './components/ScrapeButton';
import JobDetail from './components/JobDetail';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import './App.css';

const socket = io('http://127.0.0.1:5000');

function App() {
  const [jobs, setJobs] = useState([]);
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

  const handleSearch = async (query) => {
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
    <Router>
      <div className="App">
        <div className="navbar">
          <h1>JobHuntScraper</h1>
        </div>
        <div className="container">
          <SearchBar onSearch={handleSearch} />
          <ScrapeButton onScrape={handleScrape} />
          {message && <p>{message}</p>}
          <Switch>
            <Route exact path="/" component={() => <JobList jobs={jobs} />} />
            <Route path="/job/:id" component={() => <JobDetail jobs={jobs} />} />
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default App;
