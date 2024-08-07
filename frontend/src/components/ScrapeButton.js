import React, { useState } from 'react';
import { scrapeJobs } from '../services/api';

const ScrapeButton = ({ source, fetchJobs, status, onScrapeComplete, globalMessage, setGlobalMessage }) => {
  const [scraping, setScraping] = useState(false);

  const handleScrape = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token found, please log in.');
      return;
    }
    try {
      setScraping(true);
      await scrapeJobs(source.toLowerCase());  // Convert source to lowercase
      setGlobalMessage(`${source} scraping completed`);
      fetchJobs();
      onScrapeComplete();
    } catch (error) {
      console.error(`Error scraping ${source} jobs:`, error);
      setGlobalMessage(`Error scraping ${source} jobs: ${error.response ? error.response.data.message : error.message}`);
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="scrape-button">
      <button onClick={handleScrape} disabled={scraping || status} className="primary-button">
        Scrape {source}
      </button>
      {globalMessage && globalMessage.includes(source) && (
        <div className="scrape-message">
          <p>{globalMessage}</p>
        </div>
      )}
    </div>
  );
};

export default ScrapeButton;
