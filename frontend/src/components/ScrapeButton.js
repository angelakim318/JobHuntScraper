import React from 'react';

const ScrapeButton = ({ onScrape }) => {
  return (
    <button onClick={onScrape}>Scrape Jobs</button>
  );
};

export default ScrapeButton;
