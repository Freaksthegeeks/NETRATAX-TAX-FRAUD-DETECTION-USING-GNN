import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import Plot from 'react-plotly.js'
import axios from 'axios'
import './ChartCard.css'

const ChartCard = ({ title, endpoint, height = 400, fullWidth = false, customChart = false }) => {
  const [chartData, setChartData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const containerRef = useRef(null)

  useEffect(() => {
    fetchChartData()
  }, [endpoint])

  const fetchChartData = async () => {
    try {
      const response = await axios.get(endpoint)
      const plotlyData = response.data
      
      // Update colors to match palette
      if (plotlyData.data) {
        plotlyData.data = plotlyData.data.map(trace => {
          if (trace.marker) {
            trace.marker.color = trace.marker.color || 'var(--forsythia)'
          }
          if (Array.isArray(trace.marker?.color)) {
            // Handle color arrays
            trace.marker.color = trace.marker.color.map((color, idx) => {
              if (color === 'green' || color === '#27ae60') return '#114C5A'
              if (color === 'red' || color === '#e74c3c') return '#FF9932'
              if (color === 'blue' || color === '#3498db') return '#FFC801'
              return color
            })
          }
          return trace
        })
      }

      // Update layout colors
      if (plotlyData.layout) {
        plotlyData.layout.paper_bgcolor = 'rgba(0,0,0,0)'
        plotlyData.layout.plot_bgcolor = 'rgba(0,0,0,0)'
        plotlyData.layout.font = {
          ...plotlyData.layout.font,
          color: '#172B36',
          family: 'Inter, sans-serif'
        }
        plotlyData.layout.title = {
          ...plotlyData.layout.title,
          font: { color: '#172B36', size: 18, family: 'Inter, sans-serif' }
        }
      }

      setChartData(plotlyData)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching chart data:', error)
      setLoading(false)
    }
  }

  return (
    <motion.div
      className={`chart-card ${fullWidth ? 'full-width' : ''}`}
      ref={containerRef}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      whileHover={{ 
        boxShadow: "0 10px 30px rgba(17, 76, 90, 0.15)",
        y: -5
      }}
    >
      <h3>{title}</h3>
      <div className="chart-container">
        {loading ? (
          <div className="chart-loading">
            <motion.div
              className="loading-dot"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
            />
            <motion.div
              className="loading-dot"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
            />
            <motion.div
              className="loading-dot"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
            />
          </div>
        ) : chartData ? (
          <Plot
            data={chartData.data}
            layout={{
              ...chartData.layout,
              height: height,
              autosize: true,
              margin: { l: 60, r: 30, t: 40, b: 60 },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d']
            }}
            style={{ width: '100%', height: '100%' }}
          />
        ) : (
          <div className="chart-error">Failed to load chart</div>
        )}
      </div>
    </motion.div>
  )
}

export default ChartCard

