import React, { useEffect } from 'react'
import { Card, CardGrid } from '../components/Card'
import { Button } from '../components/Button'
import { Loading } from '../components/Loading'
import { useDocuments } from '../hooks/useApi'
import { useAppStore } from '../store/appStore'
import './DocumentsPage.css'

export const DocumentsPage: React.FC = () => {
  const { documents, isLoadingDocuments, documentError } = useAppStore()
  const { fetchDocuments } = useDocuments()

  useEffect(() => {
    fetchDocuments()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'status-completed'
      case 'processing':
        return 'status-processing'
      case 'failed':
        return 'status-failed'
      default:
        return 'status-pending'
    }
  }

  const getStatusLabel = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  return (
    <div className="documents-page">
      <div className="page-header">
        <h1>Your Documents</h1>
        <p>Manage and analyze your uploaded PDFs</p>
      </div>

      {isLoadingDocuments && <Loading message="Loading documents..." />}

      {documentError && (
        <div className="error-message">
          <p>Error loading documents: {documentError}</p>
          <Button
            variant="secondary"
            onClick={() => fetchDocuments()}
          >
            Try Again
          </Button>
        </div>
      )}

      {documents.length === 0 && !isLoadingDocuments && !documentError && (
        <Card variant="outlined" padding="large" className="empty-state">
          <div className="empty-content">
            <div className="empty-icon">📁</div>
            <h3>No Documents Yet</h3>
            <p>You haven't uploaded any documents yet. Upload your first PDF to get started!</p>
            <Button variant="primary">Go to Upload</Button>
          </div>
        </Card>
      )}

      {documents.length > 0 && (
        <CardGrid columns={2} gap="medium">
          {documents.map((doc) => (
            <Card
              key={doc.id}
              variant="elevated"
              padding="medium"
              interactive
              className="document-card"
            >
              <div className="doc-header">
                <div className="doc-icon">📄</div>
                <div className={`doc-status ${getStatusColor(doc.status)}`}>
                  {getStatusLabel(doc.status)}
                </div>
              </div>

              <h3 className="doc-title">{doc.filename}</h3>

              <div className="doc-meta">
                <div className="meta-item">
                  <span className="meta-label">Size:</span>
                  <span className="meta-value">
                    {(doc.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Pages:</span>
                  <span className="meta-value">{doc.pages}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Uploaded:</span>
                  <span className="meta-value">
                    {new Date(doc.upload_date).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {doc.error && (
                <div className="doc-error">
                  <p>Error: {doc.error}</p>
                </div>
              )}

              <div className="doc-actions">
                <Button
                  variant="primary"
                  size="small"
                  fullWidth
                >
                  Analyze
                </Button>
                <Button
                  variant="ghost"
                  size="small"
                  fullWidth
                >
                  View
                </Button>
              </div>
            </Card>
          ))}
        </CardGrid>
      )}
    </div>
  )
}
