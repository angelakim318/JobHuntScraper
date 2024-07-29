import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="search-bar">
      <input 
        type="text" 
        placeholder="Filter job titles..." 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
      <button type="submit">Filter</button>
    </form>
  );
};

export default SearchBar;