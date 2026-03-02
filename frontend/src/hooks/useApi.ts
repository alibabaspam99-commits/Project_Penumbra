import { useState, useCallback, useEffect } from 'react'
import { apiMethods, handleApiError, initializeApiClient } from '../api/client'
import { useAppStore } from '../store/appStore'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: { code: string; message: string } | null
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: () => Promise<T | null>
  reset: () => void
}

/**
 * Generic hook for making API calls with loading and error states
 */
export const useApi = <T,>(
  apiFunction: () => Promise<any>,
  options?: {
    onSuccess?: (data: T) => void
    onError?: (error: { code: string; message: string }) => void
    immediate?: boolean
  }
): UseApiReturn<T> => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null })

    try {
      const result = await apiFunction()
      const data = result.data || result

      setState({ data, loading: false, error: null })
      options?.onSuccess?.(data)
      return data as T
    } catch (err) {
      const error = handleApiError(err)
      setState({ data: null, loading: false, error })
      options?.onError?.(error)
      return null
    }
  }, [apiFunction, options])

  useEffect(() => {
    if (options?.immediate !== false) {
      execute()
    }
  }, [execute, options?.immediate])

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return { ...state, execute, reset }
}

/**
 * Hook for document management
 */
export const useDocuments = () => {
  const { documents, setDocuments, setLoadingDocuments, setDocumentError, addDocument } =
    useAppStore()

  const fetchDocuments = useCallback(async (skip = 0, limit = 20) => {
    setLoadingDocuments(true)
    setDocumentError(null)

    try {
      const result = await apiMethods.getDocuments(skip, limit)
      if (result.data?.documents) {
        setDocuments(result.data.documents)
      }
    } catch (err) {
      const error = handleApiError(err)
      setDocumentError(error.message)
    } finally {
      setLoadingDocuments(false)
    }
  }, [setDocuments, setLoadingDocuments, setDocumentError])

  const uploadDocument = useCallback(
    async (file: File) => {
      try {
        const result = await apiMethods.uploadDocument(file)
        if (result.data) {
          addDocument({
            id: result.data.document_id,
            filename: result.data.filename,
            size: file.size,
            pages: 0,
            upload_date: new Date().toISOString(),
            status: 'pending',
          })
          return result.data
        }
      } catch (err) {
        const error = handleApiError(err)
        setDocumentError(error.message)
        throw error
      }
    },
    [addDocument, setDocumentError]
  )

  return {
    documents,
    fetchDocuments,
    uploadDocument,
  }
}

/**
 * Hook for user profile and stats
 */
export const useUserProfile = () => {
  const { user, setUser, userStats, setUserStats } = useAppStore()
  const [loading, setLoading] = useState(false)

  const fetchProfile = useCallback(async () => {
    setLoading(true)

    try {
      const result = await apiMethods.getUserProfile()
      if (result.data) {
        setUser(result.data)
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err)
    } finally {
      setLoading(false)
    }
  }, [setUser])

  const fetchStats = useCallback(async () => {
    setLoading(true)

    try {
      const result = await apiMethods.getUserStats()
      if (result.data) {
        setUserStats(result.data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    } finally {
      setLoading(false)
    }
  }, [setUserStats])

  const updateProfile = useCallback(
    async (data: Record<string, unknown>) => {
      try {
        const result = await apiMethods.updateUserProfile(data)
        if (result.data) {
          setUser(result.data)
          return result.data
        }
      } catch (err) {
        console.error('Failed to update profile:', err)
        throw err
      }
    },
    [setUser]
  )

  return {
    user,
    userStats,
    loading,
    fetchProfile,
    fetchStats,
    updateProfile,
  }
}

/**
 * Hook for analysis operations
 */
export const useAnalysis = () => {
  const {
    currentAnalysis,
    setCurrentAnalysis,
    isAnalyzing,
    setIsAnalyzing,
    analysisProgress,
    setAnalysisProgress,
    analysisError,
    setAnalysisError,
    addAnalysisToHistory,
  } = useAppStore()

  const startAnalysis = useCallback(
    async (documentId: string, techniques: string[]) => {
      setIsAnalyzing(true)
      setAnalysisError(null)
      setAnalysisProgress(0)

      try {
        const result = await apiMethods.analyzeDocument(documentId, techniques)
        if (result.data?.analysis_id) {
          setAnalysisProgress(10)
          return result.data.analysis_id
        }
      } catch (err) {
        const error = handleApiError(err)
        setAnalysisError(error.message)
        throw error
      } finally {
        setIsAnalyzing(false)
      }
    },
    [setIsAnalyzing, setAnalysisError, setAnalysisProgress]
  )

  const getAnalysisStatus = useCallback(
    async (analysisId: string) => {
      try {
        const result = await apiMethods.getAnalysisStatus(analysisId)
        if (result.data) {
          setAnalysisProgress(result.data.progress)
          return result.data
        }
      } catch (err) {
        console.error('Failed to fetch analysis status:', err)
        throw err
      }
    },
    [setAnalysisProgress]
  )

  const getResults = useCallback(
    async (documentId: string) => {
      try {
        const result = await apiMethods.getAnalysisResults(documentId)
        if (result.data) {
          setCurrentAnalysis(result.data)
          addAnalysisToHistory(result.data)
          return result.data
        }
      } catch (err) {
        console.error('Failed to fetch analysis results:', err)
        throw err
      }
    },
    [setCurrentAnalysis, addAnalysisToHistory]
  )

  return {
    currentAnalysis,
    isAnalyzing,
    analysisProgress,
    analysisError,
    startAnalysis,
    getAnalysisStatus,
    getResults,
  }
}

/**
 * Hook for leaderboard data
 */
export const useLeaderboard = () => {
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchLeaderboard = useCallback(async (limit = 100) => {
    setLoading(true)

    try {
      const result = await apiMethods.getLeaderboard(limit)
      if (result.data) {
        setLeaderboard(Array.isArray(result.data) ? result.data : [])
      }
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    leaderboard,
    loading,
    fetchLeaderboard,
  }
}

/**
 * Hook for initialization (API client setup)
 */
export const useInitializeApi = () => {
  const { apiUrl, wsUrl } = useAppStore()

  useEffect(() => {
    // Initialize API client on mount
    initializeApiClient()
  }, [apiUrl])

  return { apiUrl, wsUrl }
}
