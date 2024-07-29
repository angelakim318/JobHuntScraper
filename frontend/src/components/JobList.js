import React from 'react';

const JobList = ({ jobs }) => {
  return (
    <div className="job-list">
      {jobs.map((job) => (
        <div key={job.id} className="job-card">
          <p><strong>Job Title:</strong> {job.title}</p>
          <p><strong>Company:</strong> {job.company}</p>
          <p><strong>Location:</strong> {job.location}</p>
        </div>
      ))}
    </div>
  );
};

export default JobList;
