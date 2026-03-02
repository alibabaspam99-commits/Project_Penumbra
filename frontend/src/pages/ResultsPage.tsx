import React from 'react'
import { ResultsView } from '../components/ResultsView'
import { Card } from '../components/Card'
import { useAppStore } from '../store/appStore'
import './ResultsPage.css'

export const ResultsPage: React.FC = () => {
  const { currentAnalysis, analysisHistory } = useAppStore()

  // Mock redactions data - in real app, would come from analysis results
  const mockRedactions = [
    {
      id: '1',
      page_number: 1,
      x: 100,
      y: 150,
      width: 200,
      height: 30,
      confidence: 0.95,
      technique: 'text_extraction',
      recovered_text: '[REDACTED]',
      status: 'verified' as const,
    },
    {
      id: '2',
      page_number: 1,
      x: 100,
      y: 200,
      width: 250,
      height: 30,
      confidence: 0.87,
      technique: 'edge_analysis',
      recovered_text: 'Hidden text recovered',
      status: 'unverified' as const,
    },
    {
      id: '3',
      page_number: 2,
      x: 80,
      y: 100,
      width: 300,
      height: 25,
      confidence: 0.92,
      technique: 'ocg_layers',
      recovered_text: 'Layer text found',
      status: 'verified' as const,
    },
  ]

  const hasResults = currentAnalysis || analysisHistory.length > 0

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Exporting results...')
  }

  const handleVerify = (redactionId: string, status: 'verified' | 'rejected') => {
    // TODO: Implement verification update
    console.log(`Redaction ${redactionId} marked as ${status}`)
  }

  return (
    <div className="results-page">
      {!hasResults && (
        <Card variant="outlined" padding="large" className="empty-state">
          <div className="empty-content">
            <div className="empty-icon">📊</div>
            <h3>No Results Yet</h3>
            <p>
              Analyze a document to see recovery results, statistics, and recovered text.
            </p>
            <p className="empty-hint">Upload and analyze a redacted PDF to get started.</p>
          </div>
        </Card>
      )}

      {hasResults && (
        <ResultsView
          documentName="Document_Name.pdf"
          pageCount={2}
          redactions={mockRedactions}
          verifiedCount={2}
          onExport={handleExport}
          onVerify={handleVerify}
        />
      )}

      {analysisHistory.length > 0 && (
        <div className="analysis-history">
          <h3>Analysis History</h3>
          <div className="history-list">
            {analysisHistory.map((analysis, index) => (
              <Card key={index} variant="outlined" padding="medium">
                <div className="history-item">
                  <div className="history-info">
                    <p className="history-date">
                      {new Date(analysis.started_at).toLocaleDateString()}
                    </p>
                    <p className="history-stats">
                      {analysis.verified_count} verified of {analysis.total_count} redactions
                    </p>
                  </div>
                  <div className="history-accuracy">
                    {analysis.total_count > 0
                      ? (
                          ((analysis.verified_count / analysis.total_count) * 100).toFixed(
                            1
                          )
                        )
                      : '0'}
                    %
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
