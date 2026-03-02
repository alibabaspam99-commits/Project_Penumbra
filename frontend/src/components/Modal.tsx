import React from 'react'
import type { ReactNode } from 'react'
import { Button } from './Button'
import './Modal.css'

interface ModalProps {
  isOpen: boolean
  title: string
  children: ReactNode
  onClose: () => void
  onConfirm?: () => void
  confirmText?: string
  cancelText?: string
  isDangerous?: boolean
  size?: 'small' | 'medium' | 'large'
  showActions?: boolean
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  title,
  children,
  onClose,
  onConfirm,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDangerous = false,
  size = 'medium',
  showActions = true,
}) => {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className={`modal modal-${size}`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">
            {title}
          </h2>
          <button
            className="modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="modal-content">{children}</div>

        {/* Actions */}
        {showActions && (
          <div className="modal-actions">
            <Button variant="ghost" size="medium" onClick={onClose}>
              {cancelText}
            </Button>
            {onConfirm && (
              <Button
                variant={isDangerous ? 'danger' : 'primary'}
                size="medium"
                onClick={() => {
                  onConfirm()
                  onClose()
                }}
              >
                {confirmText}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  isDangerous?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDangerous = false,
  onConfirm,
  onCancel,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      title={title}
      onClose={onCancel}
      onConfirm={onConfirm}
      confirmText={confirmText}
      cancelText={cancelText}
      isDangerous={isDangerous}
      size="small"
    >
      <p className="modal-message">{message}</p>
    </Modal>
  )
}

interface InfoModalProps {
  isOpen: boolean
  title: string
  children: ReactNode
  onClose: () => void
}

export const InfoModal: React.FC<InfoModalProps> = ({
  isOpen,
  title,
  children,
  onClose,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      title={title}
      onClose={onClose}
      showActions={false}
      size="medium"
    >
      {children}
    </Modal>
  )
}
