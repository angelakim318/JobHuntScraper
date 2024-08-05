import React, { useState } from 'react';

const SearchBar = ({ onSearch, locations }) => {
  const [query, setQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query, selectedLocation);
  };

  return (
    <form onSubmit={handleSearch} className="search-bar">
      <input 
        type="text" 
        placeholder="Filter job titles..." 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
      <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)}>
        <option value="">All Locations</option>
        {locations.map((location, index) => (
          <option key={index} value={location}>{location}</option>
        ))}
      </select>
      <button type="submit">Filter</button>
    </form>
  );
};

export default SearchBar;
