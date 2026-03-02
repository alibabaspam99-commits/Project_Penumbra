import React, { useRef, useState } from 'react'
import './FileUpload.css'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  accept?: string
  multiple?: boolean
  maxSize?: number // in bytes
  loading?: boolean
  error?: string
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  accept = '.pdf',
  multiple = false,
  maxSize = 100 * 1024 * 1024, // 100MB default
  loading = false,
  error,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [fileName, setFileName] = useState<string>('')

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      validateAndSelect(file)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (files && files.length > 0) {
      const file = files[0]
      validateAndSelect(file)
    }
  }

  const validateAndSelect = (file: File) => {
    // Check file type
    const validTypes = accept.split(',').map((t) => t.trim())
    const isValidType = validTypes.some(
      (type) =>
        file.type === type ||
        file.name.endsWith(type.replace('*', ''))
    )

    if (!isValidType) {
      // You might want to show an error here
      return
    }

    // Check file size
    if (file.size > maxSize) {
      // You might want to show an error here
      return
    }

    setFileName(file.name)
    onFileSelect(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileInput}
        className="file-upload-input"
        disabled={loading}
      />

      <div
        className={`file-upload-area ${dragActive ? 'drag-active' : ''} ${
          loading ? 'loading' : ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyPress={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleClick()
          }
        }}
      >
        {loading ? (
          <div className="upload-loading">
            <div className="spinner"></div>
            <p>Uploading...</p>
          </div>
        ) : fileName ? (
          <div className="upload-success">
            <div className="success-icon">✓</div>
            <p className="file-name">{fileName}</p>
            <p className="small">Click to change file</p>
          </div>
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon">📄</div>
            <p className="upload-text">
              Drag and drop your PDF here or click to browse
            </p>
            <p className="upload-hint">Maximum file size: {(maxSize / 1024 / 1024).toFixed(0)}MB</p>
          </div>
        )}
      </div>

      {error && <div className="upload-error">{error}</div>}
    </div>
  )
}
