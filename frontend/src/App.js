import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import JobList from './components/JobList';
import SearchBar from './components/SearchBar';
import ScrapeButton from './components/ScrapeButton';
import JobDetail from './components/JobDetail';
import Register from './components/Register';
import Login from './components/Login';
import { BrowserRouter as Router, Route, Switch, Redirect, useHistory } from 'react-router-dom';
import './App.css';

const socket = io('http://127.0.0.1:5000');

function App() {
  const [jobs, setJobs] = useState([]);
  const [message, setMessage] = useState('');
  const [auth, setAuth] = useState(false);
  const history = useHistory();

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
  }, [auth]);

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:5000/api/jobs', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setJobs(response.data);
      setMessage(''); // Clear message after fetching jobs
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

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
    history.push('/login');
  };

  return (
    <Router>
      <div className="App">
        <div className="navbar">
          <h1>JobHuntScraper</h1>
          {auth && <button onClick={handleLogout} className="logout-button">Logout</button>}
        </div>
        <div className="container">
          <Switch>
            <Route path="/register" component={Register} />
            <Route path="/login">
              <Login setAuth={setAuth} />
            </Route>
            {auth ? (
              <>
                <div className="scrape-button">
                  <ScrapeButton onScrape={handleScrape} />
                  <p className="scrape-message">Note: Scraping will take around 30 minutes to complete.</p>
                </div>
                <SearchBar onSearch={handleSearch} />
                {message && <p>{message}</p>}
                <Switch>
                  <Route exact path="/" component={() => <JobList jobs={jobs} />} />
                  <Route path="/job/:id" component={() => <JobDetail jobs={jobs} />} />
                </Switch>
              </>
            ) : (
              <Redirect to="/login" />
            )}
          </Switch>
        </div>
      </div>
    </Router>
  );
}

export default App;
