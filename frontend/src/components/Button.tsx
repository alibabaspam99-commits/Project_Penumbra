import React from 'react'
import './Button.css'

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  icon?: React.ReactNode
  fullWidth?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'medium',
      loading = false,
      icon,
      fullWidth = false,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const widthClass = fullWidth ? 'full-width' : ''
    const disabledClass = disabled || loading ? 'disabled' : ''

    return (
      <button
        ref={ref}
        className={`btn btn-${variant} btn-${size} ${widthClass} ${disabledClass} ${className}`}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <span className="btn-spinner"></span>
            Loading...
          </>
        ) : (
          <>
            {icon && <span className="btn-icon">{icon}</span>}
            {children}
          </>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'
