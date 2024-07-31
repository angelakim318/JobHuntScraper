import React from 'react';
import { useParams, Link } from 'react-router-dom';

const JobDetail = ({ jobs }) => {
  const { id } = useParams();
  const job = jobs.find(job => job.id === parseInt(id));

  if (!job) {
    return <div>Job not found</div>;
  }

  return (
    <div className="job-detail">
      <h2>{job.title}</h2>
      <p><strong>Company:</strong> {job.company}</p>
      <p><strong>Job Type:</strong> {job.job_type}</p>
      <p><strong>Location:</strong> {job.location}</p>
      <p><strong>Benefits:</strong> {job.benefits}</p>
      <p><strong>Posted Date:</strong> {job.posted_date}</p>
      <p><strong>Qualifications:</strong> {job.qualifications}</p>
      <p><strong>Job Description:</strong></p>
      <div dangerouslySetInnerHTML={{ __html: job.job_description }} />
      <div className="button-container">
        <Link to="/" className="back-button">Return to Listings</Link>
      </div>
    </div>
  );
};

export default JobDetail;
