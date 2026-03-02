import React, { useState } from 'react'
import { Card } from './Card'
import { Button } from './Button'
import './AnalysisPanel.css'

interface AnalysisPanelProps {
  documentName: string
  onAnalyze: (techniques: string[]) => Promise<void>
  loading?: boolean
  progress?: number
}

const AVAILABLE_TECHNIQUES = [
  {
    id: 'ocg_layers',
    name: 'OCG Layer Extraction',
    description: 'Extract hidden layers from PDF structure',
    icon: '🔍',
  },
  {
    id: 'text_extraction',
    name: 'Text Layer Analysis',
    description: 'Extract text from underlying layers',
    icon: '📝',
  },
  {
    id: 'edge_analysis',
    name: 'Edge Artifact Decoding',
    description: 'Analyze sub-pixel gradient artifacts',
    icon: '✨',
  },
  {
    id: 'width_filter',
    name: 'Width Filtering',
    description: 'Eliminate non-matching candidates',
    icon: '🎯',
  },
  {
    id: 'over_redaction',
    name: 'Over-redaction Analysis',
    description: 'Solve clusters with search strings',
    icon: '🔐',
  },
]

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  documentName,
  onAnalyze,
  loading = false,
  progress = 0,
}) => {
  const [selectedTechniques, setSelectedTechniques] = useState<string[]>([])

  const handleTechniqueToggle = (techId: string) => {
    setSelectedTechniques((prev) =>
      prev.includes(techId)
        ? prev.filter((id) => id !== techId)
        : [...prev, techId]
    )
  }

  const handleSelectAll = () => {
    if (selectedTechniques.length === AVAILABLE_TECHNIQUES.length) {
      setSelectedTechniques([])
    } else {
      setSelectedTechniques(AVAILABLE_TECHNIQUES.map((t) => t.id))
    }
  }

  const handleAnalyze = async () => {
    if (selectedTechniques.length === 0) return
    await onAnalyze(selectedTechniques)
  }

  return (
    <Card variant="elevated" padding="large">
      <div className="analysis-panel">
        <div className="panel-header">
          <h3>Analyze Document</h3>
          <p className="doc-name">{documentName}</p>
        </div>

        {loading && progress > 0 && (
          <div className="progress-section">
            <div className="progress-label">
              <span>Analysis Progress</span>
              <span className="progress-percent">{progress}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        <div className="techniques-section">
          <div className="section-header">
            <h4>Select Recovery Techniques</h4>
            <button
              className="select-all-btn"
              onClick={handleSelectAll}
              disabled={loading}
            >
              {selectedTechniques.length === AVAILABLE_TECHNIQUES.length
                ? 'Deselect All'
                : 'Select All'}
            </button>
          </div>

          <div className="techniques-grid">
            {AVAILABLE_TECHNIQUES.map((tech) => (
              <label
                key={tech.id}
                className={`technique-card ${
                  selectedTechniques.includes(tech.id) ? 'selected' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedTechniques.includes(tech.id)}
                  onChange={() => handleTechniqueToggle(tech.id)}
                  disabled={loading}
                />
                <div className="technique-content">
                  <div className="technique-icon">{tech.icon}</div>
                  <h5 className="technique-name">{tech.name}</h5>
                  <p className="technique-desc">{tech.description}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="panel-actions">
          <Button
            variant="primary"
            size="large"
            fullWidth
            loading={loading}
            disabled={selectedTechniques.length === 0 || loading}
            onClick={handleAnalyze}
          >
            {loading ? 'Analyzing...' : 'Start Analysis'}
          </Button>
        </div>
      </div>
    </Card>
  )
}
