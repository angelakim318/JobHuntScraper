import React from 'react';
import { Link } from 'react-router-dom';

const JobList = ({ jobs }) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <div key={job.id} className="job-card">
          <Link to={`/job/${job.id}`}>
            <h2>{job.title}</h2>
          </Link>
          <p>{job.company}</p>
          <p>{job.location}</p>
        </div>
      ))}
    </div>
  );
};

export default JobList;
