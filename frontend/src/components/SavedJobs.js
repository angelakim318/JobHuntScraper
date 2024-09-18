import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const SavedJobs = () => {
  const [savedJobs, setSavedJobs] = useState([]);
  const [message, setMessage] = useState('');

  // Helper function to get JWT token
  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  };

  const fetchSavedJobs = useCallback(async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/saved_jobs', getAuthHeaders()); 
      setSavedJobs(response.data);
    } catch (error) {
      console.error('Error fetching saved jobs:', error);
    }
  }, []);

  const handleDelete = async (jobId) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/api/saved_jobs/${jobId}`, getAuthHeaders()); 
      setMessage('Job deleted successfully!');
      fetchSavedJobs(); // Refresh list after deletion
    } catch (error) {
      console.error('Error deleting job:', error);
      setMessage('Error deleting job.');
    }
  };

  useEffect(() => {
    fetchSavedJobs(); 
  }, [fetchSavedJobs]);  // Added fetchSavedJobs to dependency array

  if (savedJobs.length === 0) {
    return <p>No saved jobs found.</p>;
  }

  return (
    <div className="saved-jobs-container">
      <h2>Saved Jobs</h2>
      {message && <p>{message}</p>}
      <ul>
        {savedJobs.map((job) => (
          <li key={job.id}>
            <Link to={`/job/${job.id}`} className="job-title-link">
              {job.title}
            </Link>
            <button onClick={() => handleDelete(job.id)} className="delete-button">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SavedJobs;
