import React, { useState } from 'react'
import { Card } from '../components/Card'
import { Button } from '../components/Button'
import { useAppStore } from '../store/appStore'
import './SettingsPage.css'

export const SettingsPage: React.FC = () => {
  const { setDarkMode, uiState } = useAppStore()
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [pushNotifications, setPushNotifications] = useState(true)
  const [autoAnalysis, setAutoAnalysis] = useState(false)
  const [resultsPerPage, setResultsPerPage] = useState('20')
  const [savedSettings, setSavedSettings] = useState(false)

  const handleSaveSettings = () => {
    setSavedSettings(true)
    setTimeout(() => setSavedSettings(false), 3000)
  }

  const handleToggleDarkMode = () => {
    setDarkMode(!uiState.isDarkMode)
    localStorage.setItem('penumbra-theme', !uiState.isDarkMode ? 'dark' : 'light')
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Settings & Preferences</h1>
        <p>Customize your Penumbra experience</p>
      </div>

      <div className="settings-grid">
        {/* Appearance Settings */}
        <Card title="Appearance" variant="elevated" padding="large">
          <div className="setting-item">
            <div className="setting-label">
              <h4>Dark Mode</h4>
              <p>Use dark theme for reduced eye strain</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={uiState.isDarkMode}
                onChange={handleToggleDarkMode}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Language</h4>
              <p>Choose your preferred language</p>
            </div>
            <select className="setting-select">
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
              <option>German</option>
              <option>Chinese</option>
            </select>
          </div>
        </Card>

        {/* Notification Settings */}
        <Card title="Notifications" variant="elevated" padding="large">
          <div className="setting-item">
            <div className="setting-label">
              <h4>Email Notifications</h4>
              <p>Receive updates about your analyses</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Push Notifications</h4>
              <p>Get notified when analyses complete</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={pushNotifications}
                onChange={(e) => setPushNotifications(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Weekly Digest</h4>
              <p>Receive a summary of your weekly activity</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" defaultChecked />
              <span className="slider"></span>
            </label>
          </div>
        </Card>

        {/* Analysis Settings */}
        <Card title="Analysis" variant="elevated" padding="large">
          <div className="setting-item">
            <div className="setting-label">
              <h4>Auto-Analysis</h4>
              <p>Automatically analyze PDFs on upload</p>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={autoAnalysis}
                onChange={(e) => setAutoAnalysis(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Default Techniques</h4>
              <p>Techniques to use for auto-analysis</p>
            </div>
            <div className="technique-checkboxes">
              <label>
                <input type="checkbox" defaultChecked /> Text Extraction
              </label>
              <label>
                <input type="checkbox" defaultChecked /> OCG Layers
              </label>
              <label>
                <input type="checkbox" /> Edge Analysis
              </label>
              <label>
                <input type="checkbox" /> Width Filtering
              </label>
            </div>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Results Per Page</h4>
              <p>How many results to show in tables</p>
            </div>
            <select
              className="setting-select"
              value={resultsPerPage}
              onChange={(e) => setResultsPerPage(e.target.value)}
            >
              <option>10</option>
              <option>20</option>
              <option>50</option>
              <option>100</option>
            </select>
          </div>
        </Card>

        {/* Privacy Settings */}
        <Card title="Privacy & Security" variant="elevated" padding="large">
          <div className="setting-item">
            <div className="setting-label">
              <h4>Profile Visibility</h4>
              <p>Show your profile on leaderboard</p>
            </div>
            <select className="setting-select">
              <option>Public</option>
              <option>Private</option>
              <option>Friends Only</option>
            </select>
          </div>

          <div className="divider"></div>

          <div className="setting-item">
            <div className="setting-label">
              <h4>Data Sharing</h4>
              <p>Allow analysis to be used for research</p>
            </div>
            <label className="toggle-switch">
              <input type="checkbox" defaultChecked />
              <span className="slider"></span>
            </label>
          </div>

          <div className="divider"></div>

          <div className="setting-item danger-zone">
            <div className="setting-label">
              <h4>Delete Account</h4>
              <p>Permanently delete your account and data</p>
            </div>
            <Button variant="danger" size="small">
              Delete Account
            </Button>
          </div>
        </Card>

        {/* About */}
        <Card title="About" variant="outlined" padding="large">
          <div className="about-content">
            <p>
              <strong>Penumbra v1.0.0</strong>
            </p>
            <p>
              Distributed citizen science platform for analyzing and recovering hidden text in
              redacted PDFs.
            </p>
            <div className="about-links">
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
              <a href="#contact">Contact Support</a>
              <a href="#github">GitHub</a>
            </div>
          </div>
        </Card>
      </div>

      <div className="settings-actions">
        {savedSettings && (
          <div className="saved-message">✓ Settings saved successfully</div>
        )}
        <Button variant="primary" size="large" onClick={handleSaveSettings}>
          Save All Settings
        </Button>
        <Button variant="secondary" size="large">
          Reset to Defaults
        </Button>
      </div>
    </div>
  )
}
