import React, { useEffect } from 'react'
import { Card, CardGrid } from '../components/Card'
import { Button } from '../components/Button'
import { Loading } from '../components/Loading'
import { useUserProfile } from '../hooks/useApi'
import './ProfilePage.css'

export const ProfilePage: React.FC = () => {
  const { user, userStats, loading, fetchProfile, fetchStats } = useUserProfile()

  useEffect(() => {
    fetchProfile()
    fetchStats()
  }, [])

  // Mock achievements data
  const mockAchievements = [
    { id: '1', name: 'First Steps', description: 'Complete your first PDF analysis', icon: '👣' },
    { id: '2', name: 'Data Champion', description: 'Analyze 10 documents', icon: '🏆' },
    { id: '3', name: 'Accuracy Master', description: 'Achieve 95% verification rate', icon: '⭐' },
    { id: '4', name: 'Dedicated Analyst', description: 'Analyze 100 documents', icon: '💎' },
    { id: '5', name: 'Community Leader', description: 'Reach top 10 on leaderboard', icon: '👑' },
  ]

  if (loading && !user) {
    return <Loading message="Loading profile..." />
  }

  const renderLevelBadge = (level: number) => {
    const colors = [
      '#94a3b8',
      '#d97706',
      '#3b82f6',
      '#8b5cf6',
      '#ec4899',
      '#f59e0b',
    ]
    const color = colors[Math.min(level - 1, colors.length - 1)]
    return <div className="level-badge" style={{ backgroundColor: color }}>{level}</div>
  }

  return (
    <div className="profile-page">
      {user ? (
        <>
          <div className="profile-header">
            <div className="profile-avatar">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.username} />
              ) : (
                <div className="avatar-placeholder">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              )}
            </div>

            <div className="profile-info">
              <h1>{user.username}</h1>
              <p className="profile-email">{user.email}</p>
              <p className="profile-joined">
                Joined {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>

            <div className="profile-actions">
              <Button variant="secondary" size="medium">
                Edit Profile
              </Button>
              <Button variant="ghost" size="medium">
                Settings
              </Button>
            </div>
          </div>

          {userStats && (
            <>
              <div className="stats-overview">
                <h2>Statistics</h2>

                <CardGrid columns={2} gap="medium">
                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">📚</div>
                      <div className="stat-content">
                        <div className="stat-value">{userStats.total_pdfs_processed}</div>
                        <div className="stat-label">PDFs Processed</div>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">📄</div>
                      <div className="stat-content">
                        <div className="stat-value">
                          {userStats.total_redactions_analyzed}
                        </div>
                        <div className="stat-label">Redactions Analyzed</div>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">✓</div>
                      <div className="stat-content">
                        <div className="stat-value">{userStats.verified_count}</div>
                        <div className="stat-label">Verified Results</div>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">🎯</div>
                      <div className="stat-content">
                        <div className="stat-value">{userStats.accuracy.toFixed(1)}%</div>
                        <div className="stat-label">Accuracy</div>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">🔥</div>
                      <div className="stat-content">
                        <div className="stat-value">{userStats.current_streak}</div>
                        <div className="stat-label">Current Streak</div>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="stat-box">
                      <div className="stat-icon">⭐</div>
                      <div className="stat-content">
                        <div className="stat-value">{userStats.best_streak}</div>
                        <div className="stat-label">Best Streak</div>
                      </div>
                    </div>
                  </Card>
                </CardGrid>
              </div>

              <div className="gamification-section">
                <h2>Gamification</h2>

                <CardGrid columns={2} gap="medium">
                  <Card variant="outlined" padding="medium">
                    <div className="gamification-box">
                      <div className="gamification-label">Level</div>
                      <div className="gamification-display">
                        {renderLevelBadge(userStats.level)}
                        <span className="level-text">{userStats.rank}</span>
                      </div>
                    </div>
                  </Card>

                  <Card variant="outlined" padding="medium">
                    <div className="gamification-box">
                      <div className="gamification-label">Total Points</div>
                      <div className="points-display">{userStats.total_points}</div>
                    </div>
                  </Card>
                </CardGrid>
              </div>

              <div className="achievements-section">
                <h2>Achievements</h2>

                <div className="achievements-grid">
                  {mockAchievements.map((achievement) => (
                    <Card
                      key={achievement.id}
                      variant="outlined"
                      padding="medium"
                      className="achievement-card"
                    >
                      <div className="achievement-content">
                        <div className="achievement-icon">{achievement.icon}</div>
                        <h4 className="achievement-name">{achievement.name}</h4>
                        <p className="achievement-desc">{achievement.description}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      ) : (
        <Card variant="outlined" padding="large" className="login-prompt">
          <div className="login-content">
            <div className="login-icon">🔐</div>
            <h3>Not Logged In</h3>
            <p>Sign in to view your profile and statistics.</p>
            <Button variant="primary">Sign In</Button>
          </div>
        </Card>
      )}
    </div>
  )
}
