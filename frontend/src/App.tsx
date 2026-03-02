import { useEffect } from 'react'
import './App.css'
import { useAppStore } from './store/appStore'
import { useInitializeApi } from './hooks/useApi'
import { UploadPage, DocumentsPage, ResultsPage, ProfilePage, LeaderboardPage, SettingsPage } from './pages'

function App() {
  const {
    uiState,
    setCurrentTab,
    setDarkMode,
    setMobileMenuOpen,
  } = useAppStore()

  // Initialize API
  useInitializeApi()

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('penumbra-theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

    const isDarkMode = savedTheme ? savedTheme === 'dark' : prefersDark

    setDarkMode(isDarkMode)

    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    }
  }, [])

  const handleTabChange = (tab: typeof uiState.currentTab) => {
    setCurrentTab(tab)
    setMobileMenuOpen(false)
  }

  const toggleTheme = () => {
    const newDarkMode = !uiState.isDarkMode
    setDarkMode(newDarkMode)

    localStorage.setItem('penumbra-theme', newDarkMode ? 'dark' : 'light')

    if (newDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  return (
    <div className={`app ${uiState.isDarkMode ? 'dark' : 'light'}`}>
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Penumbra</h1>
          <p className="app-subtitle">Recover Hidden Text in Redacted PDFs</p>
        </div>

        <nav className="nav-tabs">
          <button
            className={`tab ${uiState.currentTab === 'upload' ? 'active' : ''}`}
            onClick={() => handleTabChange('upload')}
          >
            Upload
          </button>
          <button
            className={`tab ${uiState.currentTab === 'analyze' ? 'active' : ''}`}
            onClick={() => handleTabChange('analyze')}
          >
            Analyze
          </button>
          <button
            className={`tab ${uiState.currentTab === 'results' ? 'active' : ''}`}
            onClick={() => handleTabChange('results')}
          >
            Results
          </button>
          <button
            className={`tab ${uiState.currentTab === 'profile' ? 'active' : ''}`}
            onClick={() => handleTabChange('profile')}
          >
            Profile
          </button>
          <button
            className={`tab ${uiState.currentTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => handleTabChange('leaderboard')}
          >
            Leaderboard
          </button>
          <button
            className={`tab ${uiState.currentTab === 'settings' ? 'active' : ''}`}
            onClick={() => handleTabChange('settings')}
          >
            Settings
          </button>
          <button className="theme-toggle" onClick={toggleTheme}>
            {uiState.isDarkMode ? '☀️' : '🌙'}
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {uiState.currentTab === 'upload' && <UploadPage />}
        {uiState.currentTab === 'analyze' && <DocumentsPage />}
        {uiState.currentTab === 'results' && <ResultsPage />}
        {uiState.currentTab === 'profile' && <ProfilePage />}
        {uiState.currentTab === 'leaderboard' && <LeaderboardPage />}
        {uiState.currentTab === 'settings' && <SettingsPage />}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>&copy; 2026 Project Penumbra. All rights reserved.</p>
        <p>Distributed citizen science platform</p>
      </footer>
    </div>
  )
}

export default App
