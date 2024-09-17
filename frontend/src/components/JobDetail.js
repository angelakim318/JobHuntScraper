import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { saveJob } from '../services/api';

const JobDetail = ({ jobs }) => {
  const { id } = useParams();
  const job = jobs.find(job => job.id === parseInt(id));
  const [message, setMessage] = useState('');


  const handleSaveJob = async () => {
    try {
      await saveJob(job.id);  
      setMessage('Job saved successfully!');
    } catch (error) {
      console.error('Error saving job:', error);
      setMessage('Error saving job.');
    }
  };

  if (!job) {
    return <div className="job-detail"><p>Job not found</p></div>;
  }

  return (
    <div className="job-detail">
      <h2 className="job-title-detail">{job.title}</h2>
      <button onClick={handleSaveJob} className="primary-button">Save Job</button>
      {message && <p>{message}</p>}
      <div className="job-info">
        <p><strong>Company:</strong><br />{job.company || 'N/A'}</p>
        <p><strong>Job Type:</strong><br />{job.job_type && job.job_type.toLowerCase() !== 'nan' ? job.job_type : 'N/A'}</p>
        <p><strong>Location:</strong><br />{job.location || 'N/A'}</p>
        <p><strong>Benefits:</strong><br />{job.benefits || 'N/A'}</p>
        <p><strong>Posted Date:</strong><br />{job.posted_date || 'N/A'}</p>
        <p><strong>Qualifications:</strong><br />{job.qualifications || 'N/A'}</p>
        <p><strong>Job Description:</strong><br /><span className="job-description" dangerouslySetInnerHTML={{ __html: job.job_description || 'N/A' }} /></p>
      </div>
      <div className="button-container">
        <Link to="/" className="back-button">Return to Listings</Link>
      </div>
    </div>
  );
};

export default JobDetail;
