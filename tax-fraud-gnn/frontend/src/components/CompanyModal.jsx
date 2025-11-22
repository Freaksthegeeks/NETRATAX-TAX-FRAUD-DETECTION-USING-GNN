import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './CompanyModal.css'

const CompanyModal = ({ company, isOpen, onClose }) => {
  if (!company) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="modal-content"
            initial={{ opacity: 0, scale: 0.9, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 50 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <button className="modal-close" onClick={onClose}>
              ×
            </button>
            <h2>Company Details</h2>
            <div className="modal-details">
              <div className="detail-row">
                <div className="detail-item">
                  <span className="detail-label">Company ID</span>
                  <span className="detail-value">{company.company_id}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Location</span>
                  <span className="detail-value">{company.location}</span>
                </div>
              </div>
              <div className="detail-row">
                <div className="detail-item">
                  <span className="detail-label">Fraud Probability</span>
                  <span className="detail-value fraud-prob">
                    {(company.fraud_probability * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Risk Level</span>
                  <span className={`risk-level risk-${company.risk_level.toLowerCase()}`}>
                    {company.risk_level}
                  </span>
                </div>
              </div>
              <div className="detail-row">
                <div className="detail-item">
                  <span className="detail-label">Turnover</span>
                  <span className="detail-value">₹{company.turnover.toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Status</span>
                  <span className={`status-badge ${company.predicted_fraud ? 'status-fraud' : 'status-normal'}`}>
                    {company.predicted_fraud ? '🚨 FRAUD' : '✅ NORMAL'}
                  </span>
                </div>
              </div>
              <div className="detail-row">
                <div className="detail-item">
                  <span className="detail-label">Invoices Sent</span>
                  <span className="detail-value">{company.outgoing_invoices || company.sent_invoice_count || 0}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Invoices Received</span>
                  <span className="detail-value">{company.incoming_invoices || company.received_invoice_count || 0}</span>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default CompanyModal

