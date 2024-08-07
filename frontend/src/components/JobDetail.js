import React from 'react';
import { useParams, Link } from 'react-router-dom';

const JobDetail = ({ jobs }) => {
  const { id } = useParams();
  const job = jobs.find(job => job.id === parseInt(id));

  if (!job) {
    return <div className="job-detail"><p>Job not found</p></div>;
  }

  return (
    <div className="job-detail">
      <h2 className="job-title-detail">{job.title}</h2>
      <div className="job-info">
        <p><strong>Company:</strong><br />{job.company}</p>
        <p><strong>Job Type:</strong><br />{job.job_type}</p>
        <p><strong>Location:</strong><br />{job.location}</p>
        <p><strong>Benefits:</strong><br />{job.benefits}</p>
        <p><strong>Posted Date:</strong><br />{job.posted_date}</p>
        <p><strong>Qualifications:</strong><br />{job.qualifications}</p>
        <p><strong>Job Description:</strong><br /><span className="job-description" dangerouslySetInnerHTML={{ __html: job.job_description || 'N/A' }} /></p>
      </div>
      <div className="button-container">
        <Link to="/" className="back-button">Return to Listings</Link>
      </div>
    </div>
  );
};

export default JobDetail;
