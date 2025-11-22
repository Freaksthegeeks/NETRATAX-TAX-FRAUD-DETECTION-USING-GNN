import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import MetricCard from '../components/MetricCard'
import ChartCard from '../components/ChartCard'
import './Dashboard.css'

const Dashboard = () => {
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

  const metrics = [
    {
      title: 'Total Companies',
      value: stats?.total_companies || 0,
      icon: '📊',
      color: 'var(--nocturnal-expedition)',
      gradient: 'linear-gradient(135deg, var(--nocturnal-expedition) 0%, var(--oceanic-noir) 100%)'
    },
    {
      title: 'High-Risk Companies',
      value: stats?.high_risk_count || 0,
      icon: '🔴',
      color: 'var(--deep-saffron)',
      gradient: 'linear-gradient(135deg, var(--deep-saffron) 0%, var(--forsythia) 100%)'
    },
    {
      title: 'Predicted Fraud',
      value: stats?.fraud_count || 0,
      icon: '⚠️',
      color: 'var(--deep-saffron)',
      gradient: 'linear-gradient(135deg, var(--deep-saffron) 0%, #ff6b6b 100%)'
    },
    {
      title: 'Average Risk Score',
      value: stats?.average_fraud_probability 
        ? `${(stats.average_fraud_probability * 100).toFixed(2)}%` 
        : '0%',
      icon: '📈',
      color: 'var(--forsythia)',
      gradient: 'linear-gradient(135deg, var(--forsythia) 0%, var(--deep-saffron) 100%)'
    }
  ]

  return (
    <div className="dashboard">
      <motion.div
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2>Overview</h2>
        <p>Real-time fraud detection statistics and risk analysis</p>
      </motion.div>

      <div className="metrics-grid">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.5 }}
          >
            <MetricCard {...metric} />
          </motion.div>
        ))}
      </div>

      <div className="charts-section">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="charts-row"
        >
          <ChartCard
            title="Fraud Distribution"
            endpoint="/api/chart/fraud_distribution"
            height={400}
          />
          <ChartCard
            title="Risk Score Distribution"
            endpoint="/api/chart/risk_distribution"
            height={400}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="charts-row"
        >
          <ChartCard
            title="Risk by Location"
            endpoint="/api/chart/risk_by_location"
            height={400}
            fullWidth
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="charts-row"
        >
          <ChartCard
            title="Company Turnover vs Fraud Risk"
            endpoint="/api/chart/turnover_vs_risk"
            height={400}
            fullWidth
          />
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard

