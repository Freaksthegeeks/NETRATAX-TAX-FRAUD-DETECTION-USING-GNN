import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import ChartCard from '../components/ChartCard'
import './Analytics.css'

const Analytics = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/statistics')
      setStats(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching stats:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <motion.div
          className="loading-spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      </div>
    )
  }

  return (
    <div className="analytics-page">
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2>📊 Network Analytics</h2>
        <p>Transaction network analysis and pattern detection</p>
      </motion.div>

      <div className="analytics-stats">
        {[
          { label: 'Total Nodes', value: stats?.total_companies || 0, icon: '🔗' },
          { label: 'Total Edges', value: stats?.total_edges || 0, icon: '📊' },
          { label: 'Network Density', value: stats?.total_edges ? (stats.total_edges / (stats.total_companies * (stats.total_companies - 1))).toFixed(4) : '0', icon: '🌐' },
          { label: 'Avg. Fraud Prob.', value: stats?.average_fraud_probability ? `${(stats.average_fraud_probability * 100).toFixed(2)}%` : '0%', icon: '📈' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">{stat.icon}</div>
            <h4>{stat.label}</h4>
            <p className="stat-number">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      <motion.div
        className="charts-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="charts-row">
          <ChartCard
            title="Top 10 Invoice Senders"
            endpoint="/api/top_senders"
            height={400}
            customChart
          />
          <ChartCard
            title="Top 10 Invoice Receivers"
            endpoint="/api/top_receivers"
            height={400}
            customChart
          />
        </div>
      </motion.div>

      {stats && (
        <motion.div
          className="risk-distribution"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h3>Risk Level Distribution</h3>
          <div className="risk-cards">
            {[
              { label: 'HIGH RISK', value: stats.high_risk_count, color: 'var(--deep-saffron)' },
              { label: 'MEDIUM RISK', value: stats.medium_risk_count, color: 'var(--forsythia)' },
              { label: 'LOW RISK', value: stats.low_risk_count, color: 'var(--nocturnal-expedition)' }
            ].map((risk, index) => (
              <motion.div
                key={risk.label}
                className="risk-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                style={{ borderTopColor: risk.color }}
              >
                <span className="risk-badge">{risk.label}</span>
                <p className="risk-value">{risk.value}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      <motion.div
        className="info-panel"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3>💡 About GNN-Based Fraud Detection</h3>
        <div className="info-content">
          <p><strong>How the Model Works:</strong></p>
          <ul>
            <li><strong>Node Features:</strong> Company turnover, invoice sent/received counts</li>
            <li><strong>Edge Features:</strong> Invoice amounts, ITC claimed</li>
            <li><strong>Architecture:</strong> Graph Convolutional Network (3 layers)</li>
            <li><strong>Detection:</strong> Identifies anomalous patterns in transaction networks</li>
          </ul>
          <p><strong>Fraud Patterns Detected:</strong></p>
          <ul>
            <li>Shell company networks (rapid creation/dissolution)</li>
            <li>Circular invoice chains (money laundering)</li>
            <li>Disproportionate ITC claims</li>
            <li>Unusual transaction patterns</li>
            <li>Connected fraud rings</li>
          </ul>
        </div>
      </motion.div>
    </div>
  )
}

export default Analytics

