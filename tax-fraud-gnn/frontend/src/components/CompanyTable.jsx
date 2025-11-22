import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import CompanyModal from './CompanyModal'
import './CompanyTable.css'

const CompanyTable = ({ companies, loading }) => {
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)

  const handleRowClick = async (companyId) => {
    try {
      const response = await axios.get(`/api/company/${companyId}`)
      setSelectedCompany(response.data)
      setModalOpen(true)
    } catch (error) {
      console.error('Error fetching company details:', error)
    }
  }

  const getRiskBadgeClass = (riskLevel) => {
    if (riskLevel.includes('HIGH')) return 'risk-high'
    if (riskLevel.includes('MEDIUM')) return 'risk-medium'
    return 'risk-low'
  }

  if (loading) {
    return (
      <div className="table-container">
        <div className="loading-state">
          <motion.div
            className="loading-spinner"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <p>Loading companies...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="table-container">
        <h3>High-Risk Companies</h3>
        <div className="table-wrapper">
          <table className="companies-table">
            <thead>
              <tr>
                <th>Company ID</th>
                <th>Location</th>
                <th>Turnover</th>
                <th>Fraud Probability</th>
                <th>Risk Level</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {companies.map((company, index) => (
                  <motion.tr
                    key={company.company_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.02 }}
                    onClick={() => handleRowClick(company.company_id)}
                    className="table-row"
                  >
                    <td>{company.company_id}</td>
                    <td>{company.location}</td>
                    <td>{company.turnover}</td>
                    <td>
                      <span className="fraud-probability">{company.fraud_probability}</span>
                    </td>
                    <td>
                      <span className={`risk-badge ${getRiskBadgeClass(company.risk_level)}`}>
                        {company.risk_level}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${company.status.includes('FRAUD') ? 'status-fraud' : 'status-normal'}`}>
                        {company.status}
                      </span>
                    </td>
                    <td>
                      <motion.button
                        className="btn-view"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                      >
                        View
                      </motion.button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
          {companies.length === 0 && (
            <div className="empty-state">
              <p>No companies found matching the filters</p>
            </div>
          )}
        </div>
      </div>

      <CompanyModal
        company={selectedCompany}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </>
  )
}

export default CompanyTable

