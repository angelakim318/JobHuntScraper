import React, { useState, useEffect } from 'react';
import { scrapeJobs } from '../services/api';
import { io } from 'socket.io-client';

const ScrapeButton = ({ source, fetchJobs, status, onScrapeComplete }) => {
  const [message, setMessage] = useState('');
  const [scraping, setScraping] = useState(false);
  const socket = io('http://127.0.0.1:5000');

  useEffect(() => {
    socket.on('scrape_progress', (data) => {
      if (data.source === source) {
        setMessage(data.message);
      }
    });

    socket.on('scrape_complete', (data) => {
      if (data.source === source) {
        setMessage(`${data.source} scraping completed`);
        setScraping(false);
        fetchJobs();
        onScrapeComplete();
        setTimeout(() => setMessage(''), 5000);
      }
    });

    socket.on('scrape_error', (data) => {
      if (data.source === source) {
        setMessage(`Error: ${data.error}`);
        setScraping(false);
      }
    });

    return () => {
      socket.off('scrape_progress');
      socket.off('scrape_complete');
      socket.off('scrape_error');
    };
  }, [fetchJobs, socket, onScrapeComplete, source]);

  const handleScrape = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token found, please log in.');
      return;
    }
    try {
      setScraping(true);
      await scrapeJobs(source.toLowerCase());  // Convert source to lowercase
    } catch (error) {
      console.error(`Error scraping ${source} jobs:`, error);
      setMessage(`Error scraping ${source} jobs: ${error.response ? error.response.data.message : error.message}`);
      setScraping(false);
    }
  };

  return (
    <div className="scrape-button">
      <button onClick={handleScrape} disabled={scraping || status} className="primary-button">
        Scrape {source}
      </button>
      {message && (
        <div className="scrape-message">
          <p>{message}</p>
        </div>
      )}
    </div>
  );
};

export default ScrapeButton;
