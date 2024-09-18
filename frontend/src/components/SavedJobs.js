import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const SavedJobs = () => {
  const [savedJobs, setSavedJobs] = useState([]);

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
      fetchSavedJobs(); // Refresh list after deletion
    } catch (error) {
      console.error('Error deleting job:', error);
    }
  };

  useEffect(() => {
    fetchSavedJobs();
  }, [fetchSavedJobs]);

  if (savedJobs.length === 0) {
    return <p>No saved jobs found.</p>;
  }

  return (
    <div className="saved-jobs-container">
      <h2>Saved Jobs</h2>
      <ul className="saved-jobs-list">
        {savedJobs.map((job) => (
          <li key={job.id} className="saved-job-item">
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
