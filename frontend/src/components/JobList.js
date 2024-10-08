import React from 'react';
import { Link } from 'react-router-dom';

const JobList = ({ jobs }) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <div key={job.id} className="job-card">
          <Link to={`/job/${job.id}`} className="job-title-link">
            <h3 className="job-title">{job.title}</h3>
          </Link>
          <p><strong>Location:</strong> {job.location}</p>
          <p><strong>Posted Date:</strong> {job.posted_date}</p>
        </div>
      ))}
    </div>
  );
};

export default JobList;
