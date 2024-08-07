import React, { useState } from 'react';

const SearchBar = ({ onSearch, onFilter, locations }) => {
  const [query, setQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('All Locations');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleFilter = (e) => {
    e.preventDefault();
    onFilter(selectedLocation);
  };

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSearch} className="search-bar">
        <input 
          type="text" 
          placeholder="Filter job titles..." 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
        />
        <button type="submit" className="primary-button">Filter Titles</button>
      </form>

      <form onSubmit={handleFilter} className="filter-bar">
        <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)}>
          <option value="All Locations">All Locations</option>
          {locations.map((location, index) => (
            <option key={index} value={location}>{location}</option>
          ))}
        </select>
        <button type="submit" className="primary-button">Filter Locations</button>
      </form>
    </div>
  );
};

export default SearchBar;
