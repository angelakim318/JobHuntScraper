import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import JobList from './components/JobList';
import SearchBar from './components/SearchBar';
import ScrapeButton from './components/ScrapeButton';
import JobDetail from './components/JobDetail';
import Register from './components/Register';
import Login from './components/Login';
import { BrowserRouter as Router, Route, Routes, Navigate, useNavigate } from 'react-router-dom';
import './App.css';

const socket = io('http://127.0.0.1:5000');

function App() {
  const [jobs, setJobs] = useState([]);
  const [message, setMessage] = useState('');
  const [auth, setAuth] = useState(false);

  const navigate = useNavigate();

  const fetchJobs = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setMessage('No token found, please log in again.');
        setAuth(false);
        navigate('/login');
        return;
      }
      const response = await axios.get('http://127.0.0.1:5000/api/jobs', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Jobs fetched from API:', response.data);
      setJobs(response.data);
      setMessage(''); // Clear message after fetching jobs
    } catch (error) {
      const errorMessage = error.response ? error.response.data.error : 'An error occurred while fetching jobs';
      console.error('Error fetching jobs:', errorMessage);
      setMessage(errorMessage);
    }
  }, [navigate]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuth(true);
    }
  }, []);

  useEffect(() => {
    if (auth) {
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
    }
  }, [auth, fetchJobs]);

  const handleSearch = async (query) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:5000/api/jobs/search', {
        params: { query },
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setJobs(response.data);
    } catch (error) {
      console.error('Error searching jobs:', error);
    }
  };

  const handleScrape = async () => {
    try {
      const token = localStorage.getItem('token');
      setMessage('Starting scraping...');
      await axios.post('http://127.0.0.1:5000/api/scrape', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Error scraping jobs:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setAuth(false);
    navigate('/login');
  };

  return (
    <div className="App">
      <div className="navbar">
        <h1>JobHuntScraper</h1>
        {auth && <button onClick={handleLogout} className="logout-button">Logout</button>}
      </div>
      <div className="container">
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login setAuth={setAuth} />} />
          {auth ? (
            <>
              <Route path="/" element={<>
                <div className="scrape-button">
                  <ScrapeButton onScrape={handleScrape} />
                  <p className="scrape-message">Note: Scraping will take around 30 minutes to complete.</p>
                </div>
                <SearchBar onSearch={handleSearch} />
                {message && <p>{message}</p>}
                <JobList jobs={jobs} />
              </>} />
              <Route path="/job/:id" element={<JobDetail jobs={jobs} />} />
            </>
          ) : (
            <Route path="*" element={<Navigate to="/login" />} />
          )}
        </Routes>
      </div>
    </div>
  );
}

function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWrapper;
