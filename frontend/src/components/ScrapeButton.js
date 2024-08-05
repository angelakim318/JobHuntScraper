import React, { useState, useEffect } from 'react';
import { scrapeJobs, clearDatabase } from '../services/api';  
import { io } from 'socket.io-client';

const ScrapeButton = ({ fetchJobs }) => {
  const [message, setMessage] = useState('');
  const [scraping, setScraping] = useState({
    remoteco: false,
    stackoverflow: false,
    simplyhired: false
  });
  const socket = io('http://127.0.0.1:5000');

  useEffect(() => {
    socket.on('scrape_progress', (data) => {
      setMessage(data.message);
    });

    socket.on('scrape_complete', (data) => {
      setMessage(`${data.source} scraping completed`);
      setScraping((prev) => ({ ...prev, [data.source]: false }));
      fetchJobs(); // Fetch the jobs after scraping is complete
      setTimeout(() => setMessage(''), 5000); // Clear message after 5 seconds
    });

    return () => {
      socket.off('scrape_progress');
      socket.off('scrape_complete');
    };
  }, [fetchJobs, socket]);

  const handleScrape = async (source) => {
    const token = localStorage.getItem('token'); 
    if (!token) {
      console.error('No token found, please log in.');
      return;
    }
    try {
      setScraping((prev) => ({ ...prev, [source]: true }));
      await scrapeJobs(source);
      setMessage(`${source} scraping has started`);
    } catch (error) {
      console.error(`Error scraping ${source} jobs:`, error);
    }
  };

  const handleClearDatabase = async () => {
    try {
      await clearDatabase();
      setMessage('Database cleared successfully');
      setScraping({
        remoteco: false,
        stackoverflow: false,
        simplyhired: false
      });
      fetchJobs(); // Fetch jobs to update the list
      setTimeout(() => setMessage(''), 5000); // Clear message after 5 seconds
    } catch (error) {
      console.error('Error clearing database:', error);
    }
  };

  return (
    <div className="scrape-button">
      <button 
        onClick={() => handleScrape('remoteco')} 
        disabled={scraping.remoteco || scraping.stackoverflow || scraping.simplyhired}
      >
        Scrape Remote.co
      </button>
      <button 
        onClick={() => handleScrape('stackoverflow')} 
        disabled={scraping.remoteco || scraping.stackoverflow || scraping.simplyhired}
      >
        Scrape StackOverflow
      </button>
      <button 
        onClick={() => handleScrape('simplyhired')} 
        disabled={scraping.remoteco || scraping.stackoverflow || scraping.simplyhired}
      >
        Scrape SimplyHired
      </button>
      <button onClick={handleClearDatabase}>Clear Database</button>
      <div className="scrape-message">
        <p>{message}</p>
      </div>
    </div>
  );
};

export default ScrapeButton;
