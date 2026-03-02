import React from 'react'
import { Card } from './Card'
import { Button } from './Button'
import './ResultsView.css'

interface Redaction {
  id: string
  page_number: number
  x: number
  y: number
  width: number
  height: number
  confidence: number
  technique: string
  recovered_text?: string
  status: 'unverified' | 'verified' | 'rejected'
}

interface ResultsViewProps {
  documentName: string
  pageCount: number
  redactions: Redaction[]
  verifiedCount: number
  onExport?: () => void
  onVerify?: (redactionId: string, status: 'verified' | 'rejected') => void
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  documentName,
  pageCount,
  redactions,
  verifiedCount,
  onExport,
  onVerify,
}) => {
  const accuracy = redactions.length > 0
    ? ((verifiedCount / redactions.length) * 100).toFixed(1)
    : '0'

  const byTechnique = redactions.reduce(
    (acc, r) => {
      acc[r.technique] = (acc[r.technique] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  const byPage = redactions.reduce(
    (acc, r) => {
      acc[r.page_number] = (acc[r.page_number] || 0) + 1
      return acc
    },
    {} as Record<number, number>
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'status-verified'
      case 'rejected':
        return 'status-rejected'
      default:
        return 'status-unverified'
    }
  }

  return (
    <div className="results-view">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <p className="doc-name">{documentName}</p>
      </div>

      <div className="results-stats">
        <Card variant="outlined" padding="medium" className="stat-card">
          <div className="stat-value">{redactions.length}</div>
          <div className="stat-label">Total Redactions</div>
        </Card>

        <Card variant="outlined" padding="medium" className="stat-card">
          <div className="stat-value">{verifiedCount}</div>
          <div className="stat-label">Verified</div>
        </Card>

        <Card variant="outlined" padding="medium" className="stat-card">
          <div className="stat-value">{accuracy}%</div>
          <div className="stat-label">Verification Rate</div>
        </Card>

        <Card variant="outlined" padding="medium" className="stat-card">
          <div className="stat-value">{pageCount}</div>
          <div className="stat-label">Pages Analyzed</div>
        </Card>
      </div>

      <div className="results-grid">
        <Card title="By Technique" variant="outlined">
          <div className="chart-data">
            {Object.entries(byTechnique).map(([technique, count]) => (
              <div key={technique} className="chart-row">
                <span className="chart-label">{technique}</span>
                <div className="chart-bar-container">
                  <div
                    className="chart-bar"
                    style={{
                      width: `${(count / redactions.length) * 100}%`,
                    }}
                  ></div>
                </div>
                <span className="chart-value">{count}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="By Page" variant="outlined">
          <div className="page-distribution">
            {Array.from({ length: pageCount }).map((_, i) => (
              <div key={i} className="page-item">
                <span className="page-number">Page {i + 1}</span>
                <span className="page-count">{byPage[i + 1] || 0}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card title="Detailed Findings" variant="outlined">
        <div className="findings-list">
          {redactions.length === 0 ? (
            <p className="no-results">No redactions found in analysis.</p>
          ) : (
            <div className="findings-table">
              <div className="table-header">
                <div className="col-page">Page</div>
                <div className="col-technique">Technique</div>
                <div className="col-confidence">Confidence</div>
                <div className="col-status">Status</div>
                <div className="col-text">Recovered Text</div>
                <div className="col-actions">Actions</div>
              </div>

              {redactions.map((redaction) => (
                <div key={redaction.id} className="table-row">
                  <div className="col-page">{redaction.page_number}</div>
                  <div className="col-technique">{redaction.technique}</div>
                  <div className="col-confidence">
                    <div className="confidence-badge">
                      {(redaction.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className={`col-status ${getStatusColor(redaction.status)}`}>
                    {redaction.status}
                  </div>
                  <div className="col-text">
                    {redaction.recovered_text || '—'}
                  </div>
                  <div className="col-actions">
                    {onVerify && redaction.status === 'unverified' && (
                      <div className="action-buttons">
                        <button
                          className="action-btn verify-btn"
                          onClick={() => onVerify(redaction.id, 'verified')}
                          title="Verify"
                        >
                          ✓
                        </button>
                        <button
                          className="action-btn reject-btn"
                          onClick={() => onVerify(redaction.id, 'rejected')}
                          title="Reject"
                        >
                          ✗
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {onExport && (
        <div className="results-actions">
          <Button variant="primary" onClick={onExport}>
            Export Results
          </Button>
        </div>
      )}
    </div>
  )
}
