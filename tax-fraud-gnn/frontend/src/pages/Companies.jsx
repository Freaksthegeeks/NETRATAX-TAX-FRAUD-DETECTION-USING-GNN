import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import CompanyTable from '../components/CompanyTable'
import FilterPanel from '../components/FilterPanel'
import './Companies.css'

const Companies = () => {
  const [companies, setCompanies] = useState([])
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    riskThreshold: 0.5,
    location: [],
    search: ''
  })
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchLocations()
    fetchStats()
  }, [])

  useEffect(() => {
    fetchCompanies()
  }, [filters])

  const fetchLocations = async () => {
    try {
      const response = await axios.get('/api/locations')
      setLocations(response.data)
    } catch (error) {
      console.error('Error fetching locations:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/statistics')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchCompanies = async () => {
    setLoading(true)
    try {
      const params = {
        risk_threshold: filters.riskThreshold,
        location: filters.location.join(','),
        search: filters.search
      }
      const response = await axios.get('/api/companies', { params })
      setCompanies(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching companies:', error)
      setLoading(false)
    }
  }

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
  }

  return (
    <div className="companies-page">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2>🔍 Company Fraud Analysis</h2>
        <p>Search and analyze individual companies for fraud risk</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <FilterPanel
          filters={filters}
          locations={locations}
          onFilterChange={handleFilterChange}
        />
      </motion.div>

      {stats && (
        <motion.div
          className="stats-row"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <motion.div
            className="stat-box"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <span className="stat-label">Total Companies</span>
            <span className="stat-value">{stats.total_companies}</span>
          </motion.div>
          <motion.div
            className="stat-box stat-high-risk"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <span className="stat-label">High-Risk</span>
            <span className="stat-value">{stats.high_risk_count}</span>
          </motion.div>
          <motion.div
            className="stat-box stat-medium-risk"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <span className="stat-label">Medium-Risk</span>
            <span className="stat-value">{stats.medium_risk_count}</span>
          </motion.div>
          <motion.div
            className="stat-box stat-low-risk"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <span className="stat-label">Low-Risk</span>
            <span className="stat-value">{stats.low_risk_count}</span>
          </motion.div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <CompanyTable companies={companies} loading={loading} />
      </motion.div>
    </div>
  )
}

export default Companies

