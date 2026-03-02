import React, { useState } from 'react'
import { FileUpload } from '../components/FileUpload'
import { Card } from '../components/Card'
import { Button } from '../components/Button'
import { useDocuments } from '../hooks/useApi'
import { useAppStore } from '../store/appStore'
import './UploadPage.css'

export const UploadPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadError, setUploadError] = useState<string>('')
  const [isUploading, setIsUploading] = useState(false)

  const { uploadDocument } = useDocuments()
  const { addNotification } = useAppStore()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setUploadError('')
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file first')
      return
    }

    setIsUploading(true)
    setUploadError('')

    try {
      await uploadDocument(selectedFile)
      addNotification('success', `Successfully uploaded ${selectedFile.name}`)
      setSelectedFile(null)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed'
      setUploadError(message)
      addNotification('error', `Upload failed: ${message}`)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1>Upload PDF Documents</h1>
        <p>Upload redacted PDFs to begin the analysis process</p>
      </div>

      <div className="upload-container">
        <Card variant="elevated" padding="large">
          <FileUpload
            onFileSelect={handleFileSelect}
            accept=".pdf"
            maxSize={100 * 1024 * 1024}
            loading={isUploading}
            error={uploadError}
          />

          {selectedFile && (
            <div className="upload-actions">
              <Button
                variant="primary"
                size="large"
                loading={isUploading}
                onClick={handleUpload}
                fullWidth
              >
                {isUploading ? 'Uploading...' : 'Upload PDF'}
              </Button>
              <Button
                variant="ghost"
                size="large"
                onClick={() => setSelectedFile(null)}
                disabled={isUploading}
                fullWidth
              >
                Clear Selection
              </Button>
            </div>
          )}
        </Card>
      </div>

      <div className="upload-info">
        <Card title="How it works" variant="outlined">
          <ol className="info-list">
            <li>
              <strong>Upload:</strong> Select a redacted PDF from your device
            </li>
            <li>
              <strong>Analyze:</strong> Our techniques extract hidden text from the redactions
            </li>
            <li>
              <strong>Review:</strong> Examine recovered text and verify results
            </li>
            <li>
              <strong>Submit:</strong> Contribute verified data to the database
            </li>
          </ol>
        </Card>

        <Card title="Supported Format" variant="outlined">
          <div className="info-content">
            <p>
              <strong>File Type:</strong> PDF (.pdf)
            </p>
            <p>
              <strong>Maximum Size:</strong> 100 MB
            </p>
            <p>
              <strong>Requirements:</strong> PDF must contain at least one redacted section
            </p>
          </div>
        </Card>

        <Card title="Features" variant="outlined">
          <div className="features-grid">
            <div className="feature-item">
              <span className="feature-icon">🔍</span>
              <p>OCG Layer Extraction</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📝</span>
              <p>Text Layer Analysis</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">✨</span>
              <p>Edge Artifact Decoding</p>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🎯</span>
              <p>Width Filtering</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
