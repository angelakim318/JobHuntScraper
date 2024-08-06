import React, { useState, useEffect, useCallback } from 'react';
import { getJobs, searchJobs, clearDatabase, getScrapeStatus } from './services/api';
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
  const [locations, setLocations] = useState([]);
  const [scrapeStatus, setScrapeStatus] = useState({});

  const navigate = useNavigate();

  const fetchJobs = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      const response = await getJobs();
      setJobs(response.data);
      const uniqueLocations = [...new Set(response.data.map(job => job.location))];
      setLocations(uniqueLocations);
    } catch (error) {
      const errorMessage = error.response ? error.response.data.error : 'An error occurred while fetching jobs';
      console.error('Error fetching jobs:', errorMessage);
    }
  }, [navigate]);

  const fetchScrapeStatus = useCallback(async () => {
    try {
      const response = await getScrapeStatus();
      setScrapeStatus(response.data);
    } catch (error) {
      console.error('Error fetching scrape status:', error);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuth(true);
    }
  }, []);

  useEffect(() => {
    if (auth) {
      fetchJobs();
      fetchScrapeStatus();
    }
  }, [auth, fetchJobs, fetchScrapeStatus]);

  const handleSearch = async (query, location) => {
    try {
      const response = await searchJobs(query, location);
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

  const handleClearDatabase = async () => {
    try {
      await clearDatabase();
      setJobs([]);
      fetchScrapeStatus(); // Fetch scrape status after clearing database
    } catch (error) {
      console.error('Error clearing database:', error);
    }
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
                <div className="scrape-buttons">
                  <ScrapeButton source="remoteco" fetchJobs={fetchJobs} status={scrapeStatus.remoteco} />
                  <ScrapeButton source="stackoverflow" fetchJobs={fetchJobs} status={scrapeStatus.stackoverflow} />
                  <ScrapeButton source="simplyhired" fetchJobs={fetchJobs} status={scrapeStatus.simplyhired} />
                  <button onClick={handleClearDatabase} className="clear-button">Clear Database</button>
                </div>
                <SearchBar onSearch={handleSearch} locations={locations} />
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
