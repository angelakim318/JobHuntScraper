import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { saveJob, getSavedJobs } from '../services/api';

const JobDetail = ({ jobs }) => {
  const { id } = useParams();
  const job = jobs.find(job => job.id === parseInt(id));
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    const checkIfSaved = async () => {
      try {
        const savedJobsResponse = await getSavedJobs();
        const savedJobs = savedJobsResponse.data;
        const jobIsSaved = savedJobs.some(savedJob => savedJob.id === job.id);
        setIsSaved(jobIsSaved);
      } catch (error) {
        console.error('Error checking saved jobs:', error);
      }
    };

    checkIfSaved();
  }, [job]);

  const handleSaveJob = async () => {
    if (!isSaved) {
      try {
        await saveJob(job.id);
        setIsSaved(true); // Mark the job as saved
      } catch (error) {
        console.error('Error saving job:', error);
      }
    }
  };

  if (!job) {
    return <div className="job-detail"><p>Job not found</p></div>;
  }

  return (
    <div className="job-detail">
      <h2 className="job-title-detail">{job.title}</h2>
      <div className="save-job-container">
        <button 
          onClick={handleSaveJob} 
          className={`primary-button ${isSaved ? 'saved-button' : ''}`}
          disabled={isSaved} // Disable button if the job is already saved
        >
          {isSaved ? 'Saved' : 'Save Job'}
        </button>
      </div>
      <div className="job-info">
        <p><strong>Company:</strong><br />{job.company || 'N/A'}</p>
        <p><strong>Job Type:</strong><br />{job.job_type && job.job_type.toLowerCase() !== 'nan' ? job.job_type : 'N/A'}</p>
        <p><strong>Location:</strong><br />{job.location || 'N/A'}</p>
        <p><strong>Benefits:</strong><br />{job.benefits || 'N/A'}</p>
        <p><strong>Posted Date:</strong><br />{job.posted_date || 'N/A'}</p>
        <p><strong>Qualifications:</strong><br />{job.qualifications || 'N/A'}</p>
        <p><strong>Job Description:</strong><br /><span className="job-description" dangerouslySetInnerHTML={{ __html: job.job_description || 'N/A' }} /></p>
      </div>
    </div>
  );
};

export default JobDetail;
