import React, { useEffect, useState } from 'react'
import { Card } from '../components/Card'
import { Loading } from '../components/Loading'
import { useLeaderboard } from '../hooks/useApi'
import './LeaderboardPage.css'

interface LeaderboardEntry {
  rank: number
  user_id: string
  username: string
  avatar_url?: string
  points: number
  pdfs_processed: number
  accuracy: number
}

export const LeaderboardPage: React.FC = () => {
  const { leaderboard, loading, fetchLeaderboard } = useLeaderboard()
  const [timeframe, setTimeframe] = useState<'all_time' | 'monthly' | 'weekly'>('all_time')

  useEffect(() => {
    fetchLeaderboard(100)
  }, [timeframe])

  // Mock leaderboard data
  const mockLeaderboard: LeaderboardEntry[] = [
    {
      rank: 1,
      user_id: '1',
      username: 'AnalysisMaster',
      points: 15240,
      pdfs_processed: 245,
      accuracy: 94.5,
    },
    {
      rank: 2,
      user_id: '2',
      username: 'DataDriven',
      points: 12890,
      pdfs_processed: 198,
      accuracy: 91.2,
    },
    {
      rank: 3,
      user_id: '3',
      username: 'AccuracyFirst',
      points: 11560,
      pdfs_processed: 156,
      accuracy: 96.8,
    },
    {
      rank: 4,
      user_id: '4',
      username: 'VolunteerPro',
      points: 10230,
      pdfs_processed: 142,
      accuracy: 89.3,
    },
    {
      rank: 5,
      user_id: '5',
      username: 'TextRecovery',
      points: 9145,
      pdfs_processed: 128,
      accuracy: 92.1,
    },
  ]

  const getRankMedal = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇'
      case 2:
        return '🥈'
      case 3:
        return '🥉'
      default:
        return `#${rank}`
    }
  }

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'rank-gold'
      case 2:
        return 'rank-silver'
      case 3:
        return 'rank-bronze'
      default:
        return 'rank-default'
    }
  }

  if (loading && leaderboard.length === 0) {
    return <Loading message="Loading leaderboard..." />
  }

  const displayData = leaderboard.length > 0 ? leaderboard : mockLeaderboard

  return (
    <div className="leaderboard-page">
      <div className="page-header">
        <h1>Leaderboard</h1>
        <p>Top contributors to Project Penumbra</p>
      </div>

      <div className="leaderboard-controls">
        <div className="timeframe-selector">
          <button
            className={`timeframe-btn ${timeframe === 'weekly' ? 'active' : ''}`}
            onClick={() => setTimeframe('weekly')}
          >
            This Week
          </button>
          <button
            className={`timeframe-btn ${timeframe === 'monthly' ? 'active' : ''}`}
            onClick={() => setTimeframe('monthly')}
          >
            This Month
          </button>
          <button
            className={`timeframe-btn ${timeframe === 'all_time' ? 'active' : ''}`}
            onClick={() => setTimeframe('all_time')}
          >
            All Time
          </button>
        </div>
      </div>

      <div className="leaderboard-container">
        {/* Top 3 Featured */}
        {displayData.slice(0, 3).length > 0 && (
          <div className="top-three">
            {displayData.slice(0, 3).map((entry) => (
              <Card
                key={entry.user_id}
                variant="elevated"
                padding="large"
                className={`top-card ${getRankColor(entry.rank)}`}
              >
                <div className="top-card-content">
                  <div className="medal">{getRankMedal(entry.rank)}</div>

                  <div className="avatar-circle">
                    {entry.avatar_url ? (
                      <img src={entry.avatar_url} alt={entry.username} />
                    ) : (
                      <div className="avatar-initial">
                        {entry.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>

                  <h3 className="username">{entry.username}</h3>

                  <div className="top-stats">
                    <div className="top-stat">
                      <span className="stat-value">{entry.points}</span>
                      <span className="stat-label">Points</span>
                    </div>
                    <div className="divider"></div>
                    <div className="top-stat">
                      <span className="stat-value">{entry.accuracy.toFixed(1)}%</span>
                      <span className="stat-label">Accuracy</span>
                    </div>
                  </div>

                  <div className="top-footer">
                    {entry.pdfs_processed} PDFs analyzed
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Full List */}
        <Card title="Rankings" variant="outlined">
          <div className="leaderboard-table">
            <div className="table-header">
              <div className="col-rank">Rank</div>
              <div className="col-user">User</div>
              <div className="col-points">Points</div>
              <div className="col-pdfs">PDFs</div>
              <div className="col-accuracy">Accuracy</div>
            </div>

            {displayData.map((entry) => (
              <div
                key={entry.user_id}
                className={`table-row ${getRankColor(entry.rank)}`}
              >
                <div className="col-rank">
                  <span className="rank-badge">{getRankMedal(entry.rank)}</span>
                </div>
                <div className="col-user">
                  <div className="user-info">
                    {entry.avatar_url ? (
                      <img src={entry.avatar_url} alt={entry.username} />
                    ) : (
                      <div className="avatar-initial-small">
                        {entry.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span>{entry.username}</span>
                  </div>
                </div>
                <div className="col-points">
                  <strong>{entry.points}</strong>
                </div>
                <div className="col-pdfs">{entry.pdfs_processed}</div>
                <div className="col-accuracy">
                  <div className="accuracy-badge">{entry.accuracy.toFixed(1)}%</div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Stats Section */}
        <div className="leaderboard-stats">
          <Card variant="outlined" padding="medium">
            <div className="stat-box">
              <span className="stat-icon">👥</span>
              <div className="stat-content">
                <div className="stat-number">{displayData.length}</div>
                <div className="stat-title">Total Contributors</div>
              </div>
            </div>
          </Card>

          <Card variant="outlined" padding="medium">
            <div className="stat-box">
              <span className="stat-icon">📊</span>
              <div className="stat-content">
                <div className="stat-number">
                  {displayData.reduce((sum, e) => sum + e.pdfs_processed, 0)}
                </div>
                <div className="stat-title">PDFs Analyzed</div>
              </div>
            </div>
          </Card>

          <Card variant="outlined" padding="medium">
            <div className="stat-box">
              <span className="stat-icon">🎯</span>
              <div className="stat-content">
                <div className="stat-number">
                  {(
                    displayData.reduce((sum, e) => sum + e.accuracy, 0) /
                    displayData.length
                  ).toFixed(1)}
                  %
                </div>
                <div className="stat-title">Avg Accuracy</div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
