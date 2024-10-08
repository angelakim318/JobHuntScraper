import React, { useState, useEffect, useCallback } from 'react';
import { getJobs, searchJobs, filterJobs, clearDatabase, getScrapeStatus } from './services/api';
import JobList from './components/JobList';
import SearchBar from './components/SearchBar';
import ScrapeButton from './components/ScrapeButton';
import JobDetail from './components/JobDetail';
import Register from './components/Register';
import Login from './components/Login';
import SavedJobs from './components/SavedJobs';
import { BrowserRouter as Router, Route, Routes, Navigate, useNavigate, Link } from 'react-router-dom';
import './App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [auth, setAuth] = useState(false);
  const [locations, setLocations] = useState([]);
  const [scrapeStatus, setScrapeStatus] = useState({});
  const [firstName, setFirstName] = useState('');

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
      console.log('Fetch scrape status response:', response.data);
      setScrapeStatus(response.data);
    } catch (error) {
      console.error('Error fetching scrape status:', error);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuth(true);
      const userFirstName = localStorage.getItem('firstName');
      if (userFirstName) {
        setFirstName(userFirstName.charAt(0).toUpperCase() + userFirstName.slice(1).toLowerCase());
      }
    }
  }, []);

  useEffect(() => {
    if (auth) {
      fetchJobs();
      fetchScrapeStatus();
    }
  }, [auth, fetchJobs, fetchScrapeStatus]);

  const handleSearch = async (query) => {
    try {
      const response = await searchJobs(query);
      setJobs(response.data);
    } catch (error) {
      console.error('Error searching jobs:', error);
    }
  };

  const handleFilter = async (location) => {
    try {
      const response = await filterJobs(location);
      setJobs(response.data);
    } catch (error) {
      console.error('Error filtering jobs:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('firstName');
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

  console.log('App render:', scrapeStatus);

  return (
    <div className="App">
      <div className="navbar">
        <Link to="/" className="navbar-title">
          JobHuntScraper
        </Link>
        {auth && (
          <div className="navbar-buttons">
            <Link to="/saved_jobs" className="savedJobs">My Jobs</Link> 
            <button onClick={handleLogout} className="logout-button">Logout</button>
          </div>
        )}
      </div>
      <div className="container">
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login setAuth={setAuth} setFirstName={setFirstName} />} />
          {auth ? (
            <>
              <Route path="/" element={<>
                <div className="instruction-text">
                  <span className="welcome">{`Welcome ${firstName.charAt(0).toUpperCase() + firstName.slice(1)}!`}</span><br/><br/>
                  Use the scrape buttons below to collect job postings from <em>Remote.co</em>, <em>Stackoverflow.jobs</em>, and <em>SimplyHired</em>. Save jobs that you’re interested in by clicking "Save Job" on the job's details page. You can access your saved jobs anytime by clicking the "My Jobs" button. To refresh the job listings, click <em>Clear Database</em>.
                </div>
                <div className="scrape-buttons">
                  <button onClick={handleClearDatabase} className="primary-button clear-button">Clear Database</button>
                </div>
                <div className="scrape-buttons">
                  <ScrapeButton source="remoteco" fetchJobs={fetchJobs} status={scrapeStatus.remoteco} onScrapeComplete={fetchScrapeStatus} />
                  <ScrapeButton source="stackoverflow" fetchJobs={fetchJobs} status={scrapeStatus.stackoverflow} onScrapeComplete={fetchScrapeStatus} />
                  <ScrapeButton source="simplyhired" fetchJobs={fetchJobs} status={scrapeStatus.simplyhired} onScrapeComplete={fetchScrapeStatus} />
                </div>
                <SearchBar onSearch={handleSearch} onFilter={handleFilter} locations={locations} />
                <JobList jobs={jobs} />
              </>} />
              <Route path="/job/:id" element={<JobDetail jobs={jobs} />} />
              <Route path="/saved_jobs" element={<SavedJobs />} />
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
