import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import JobList from './components/JobList';
import SearchBar from './components/SearchBar';
import ScrapeButton from './components/ScrapeButton';
import JobDetail from './components/JobDetail';
import Register from './components/Register';
import Login from './components/Login';
import { BrowserRouter as Router, Route, Routes, Navigate, useNavigate } from 'react-router-dom';
import './App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [auth, setAuth] = useState(false);

  const navigate = useNavigate();

  const fetchJobs = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      console.log('Fetching jobs with token:', token);
      const response = await axios.get('http://127.0.0.1:5000/api/jobs', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Jobs fetched from API:', response.data);
      setJobs(response.data);
    } catch (error) {
      const errorMessage = error.response ? error.response.data.error : 'An error occurred while fetching jobs';
      console.error('Error fetching jobs:', errorMessage);
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
                  <ScrapeButton fetchJobs={fetchJobs} />
                  <p className="scrape-note">Note: Scraping will take around 30 minutes to complete.</p>
                </div>
                <SearchBar onSearch={handleSearch} />
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
