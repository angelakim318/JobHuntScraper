import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../services/api';

const Login = ({ setAuth, setFirstName }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await login(username, password);

      if (response && response.data && response.data.access_token) {
        setAuth(true);
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('firstName', response.data.first_name); 
        setFirstName(response.data.first_name); 
        navigate('/');
      } else {
        setMessage('Login failed: Invalid response from server.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setMessage(error.response ? error.response.data.msg : 'An error occurred during login.');
    }
  };

  return (
    <div className="auth-wrapper">
      <p className="intro-text">
      This is <em>JobHuntScraper</em>, a web application that allows you to scrape job listings from <em>Remote.co</em>, <em>Stackoverflow.jobs</em>, and <em>SimplyHired</em> into one convenient location. You can save jobs that interest you and access them later through your personalized "My Jobs" list. Start scraping, view job listings, filter by job title or location, and manage your saved jobs. Please register and/or log in to get started.
      </p>
      <div className="auth-container">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>
        {message && <p>{message}</p>}
        <p>
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
