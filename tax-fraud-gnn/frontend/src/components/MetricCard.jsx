import React from 'react'
import { motion } from 'framer-motion'
import './MetricCard.css'

const MetricCard = ({ title, value, icon, gradient }) => {
  return (
    <motion.div
      className="metric-card"
      whileHover={{ 
        scale: 1.05,
        y: -10,
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.2)"
      }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ 
        type: "spring",
        stiffness: 200,
        damping: 15
      }}
    >
      <div 
        className="metric-card-gradient"
        style={{ background: gradient }}
      />
      <div className="metric-content">
        <motion.div
          className="metric-icon"
          animate={{ 
            rotate: [0, 10, -10, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            repeatDelay: 3
          }}
        >
          {icon}
        </motion.div>
        <motion.div
          className="metric-value"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {value}
        </motion.div>
        <div className="metric-label">{title}</div>
      </div>
      <motion.div
        className="metric-shine"
        animate={{
          x: ['-100%', '200%']
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          repeatDelay: 2,
          ease: "easeInOut"
        }}
      />
    </motion.div>
  )
}

export default MetricCard

