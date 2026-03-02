import React from 'react'
import './Card.css'

interface CardProps {
  children: React.ReactNode
  className?: string
  title?: string
  subtitle?: string
  onClick?: () => void
  variant?: 'default' | 'outlined' | 'elevated'
  padding?: 'small' | 'medium' | 'large'
  interactive?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  onClick,
  variant = 'default',
  padding = 'medium',
  interactive = false,
}) => {
  const interactiveClass = interactive || onClick ? 'interactive' : ''

  return (
    <div
      className={`card card-${variant} card-padding-${padding} ${interactiveClass} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyPress={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onClick()
              }
            }
          : undefined
      }
    >
      {(title || subtitle) && (
        <div className="card-header">
          {title && <h3 className="card-title">{title}</h3>}
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
        </div>
      )}
      <div className="card-content">{children}</div>
    </div>
  )
}

interface CardGridProps {
  children: React.ReactNode
  columns?: 1 | 2 | 3 | 4
  gap?: 'small' | 'medium' | 'large'
}

export const CardGrid: React.FC<CardGridProps> = ({
  children,
  columns = 2,
  gap = 'medium',
}) => {
  return (
    <div className={`card-grid card-grid-cols-${columns} card-grid-gap-${gap}`}>
      {children}
    </div>
  )
}
