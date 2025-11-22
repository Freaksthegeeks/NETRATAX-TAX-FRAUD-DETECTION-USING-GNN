import React from 'react'
import { motion } from 'framer-motion'
import './FilterPanel.css'

const FilterPanel = ({ filters, locations, onFilterChange }) => {
  const handleThresholdChange = (e) => {
    onFilterChange({ riskThreshold: parseFloat(e.target.value) })
  }

  const handleLocationChange = (e) => {
    const selected = Array.from(e.target.selectedOptions, option => option.value)
    onFilterChange({ location: selected })
  }

  const handleSearchChange = (e) => {
    onFilterChange({ search: e.target.value })
  }

  const handleReset = () => {
    onFilterChange({
      riskThreshold: 0.5,
      location: [],
      search: ''
    })
  }

  return (
    <motion.div
      className="filter-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="filter-group">
        <label htmlFor="riskThreshold">
          Risk Threshold: <span className="threshold-value">{filters.riskThreshold.toFixed(2)}</span>
        </label>
        <input
          type="range"
          id="riskThreshold"
          min="0"
          max="1"
          step="0.05"
          value={filters.riskThreshold}
          onChange={handleThresholdChange}
          className="slider"
        />
      </div>

      <div className="filter-group">
        <label htmlFor="locationFilter">Location:</label>
        <select
          id="locationFilter"
          multiple
          value={filters.location}
          onChange={handleLocationChange}
          className="select-multiple"
        >
          {locations.map(loc => (
            <option key={loc} value={loc}>{loc}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="companySearch">Search Company ID:</label>
        <input
          type="text"
          id="companySearch"
          placeholder="Enter company ID"
          value={filters.search}
          onChange={handleSearchChange}
          className="search-input"
        />
      </div>

      <motion.button
        className="btn-reset"
        onClick={handleReset}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Reset Filters
      </motion.button>
    </motion.div>
  )
}

export default FilterPanel

