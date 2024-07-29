import React from 'react';

const ScrapeButton = ({ onScrape }) => {
  return (
    <div className="scrape-button">
      <button onClick={onScrape}>Scrape Jobs</button>
    </div>
  );
};

export default ScrapeButton;
