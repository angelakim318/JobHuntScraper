import React, { useState } from 'react';
import { scrapeJobs } from '../services/api';

const ScrapeButton = ({ source, fetchJobs, status, onScrapeComplete }) => {
  const [message, setMessage] = useState('');
  const [scraping, setScraping] = useState(false);

  const handleScrape = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token found, please log in.');
      return;
    }
    try {
      setScraping(true);
      await scrapeJobs(source.toLowerCase());
      setMessage(`${source} scraping completed`);
      setScraping(false);
      fetchJobs();
      onScrapeComplete();
      setTimeout(() => setMessage(''), 5000);
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
