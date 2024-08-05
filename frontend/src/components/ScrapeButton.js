import React, { useState, useEffect } from 'react';
import { scrapeJobs } from '../services/api';  
import { io } from 'socket.io-client';

const ScrapeButton = ({ source, fetchJobs }) => {
  const [message, setMessage] = useState('');
  const [scraping, setScraping] = useState(false);
  const socket = io('http://127.0.0.1:5000');

  useEffect(() => {
    socket.on('scrape_progress', (data) => {
      setMessage(data.message);
    });

    socket.on('scrape_complete', (data) => {
      setMessage(`${data.source} scraping completed`);
      setScraping(false);
      fetchJobs(); // Fetch jobs after scraping is complete
      setTimeout(() => setMessage(''), 5000); // Clear message after 5 seconds
    });

    return () => {
      socket.off('scrape_progress');
      socket.off('scrape_complete');
    };
  }, [fetchJobs, socket]);

  const handleScrape = async () => {
    const token = localStorage.getItem('token'); 
    if (!token) {
      console.error('No token found, please log in.');
      return;
    }
    try {
      setScraping(true);
      const response = await scrapeJobs(source.toLowerCase());  // Convert source to lowercase
      setMessage(response.data.message);
      fetchJobs();
    } catch (error) {
      console.error(`Error scraping ${source} jobs:`, error);
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="scrape-button">
      <button onClick={handleScrape} disabled={scraping}>
        Scrape {source}
      </button>
      <div className="scrape-message">
        <p>{message}</p>
      </div>
    </div>
  );
};

export default ScrapeButton;
