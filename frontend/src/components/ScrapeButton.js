import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';

const ScrapeButton = ({ fetchJobs }) => {
  const [message, setMessage] = useState('');
  const socket = io('http://127.0.0.1:5000');

  useEffect(() => {
    socket.on('scrape_progress', (data) => {
      setMessage(data.message);
    });

    socket.on('scrape_complete', () => {
      setMessage('Scraping completed');
      fetchJobs(); // Fetch the jobs after scraping is complete
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
      const response = await axios.post('http://127.0.0.1:5000/api/scrape', {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log(response.data);
      setMessage('Scraping has started');
    } catch (error) {
      console.error('Error scraping jobs:', error);
    }
  };

  return (
    <div className="scrape-button">
      <button onClick={handleScrape}>Scrape Jobs</button>
      <div className="scrape-message">
        <p>{message}</p>
      </div>
    </div>
  );
};

export default ScrapeButton;
