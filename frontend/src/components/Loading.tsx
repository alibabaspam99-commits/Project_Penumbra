import React from 'react'
import './Loading.css'

interface LoadingProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
}

export const Loading: React.FC<LoadingProps> = ({
  message = 'Loading...',
  size = 'medium',
}) => {
  return (
    <div className={`loading-container loading-${size}`}>
      <div className="spinner"></div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  )
}

export const FullPageLoading: React.FC<{ message?: string }> = ({
  message = 'Processing...',
}) => {
  return (
    <div className="fullpage-loading">
      <Loading message={message} size="large" />
    </div>
  )
}
