import axios, { AxiosError } from 'axios'
import type { AxiosInstance } from 'axios'
import type { APIResponse } from '../types'
import { useAppStore } from '../store/appStore'

let apiClient: AxiosInstance | null = null

export const initializeApiClient = () => {
  const apiUrl = useAppStore.getState().apiUrl

  apiClient = axios.create({
    baseURL: apiUrl,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor
  apiClient.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor
  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Clear auth and redirect to login
        localStorage.removeItem('auth_token')
        useAppStore.getState().logout()
        window.location.href = '/'
      }
      return Promise.reject(error)
    }
  )

  return apiClient
}

export const getApiClient = (): AxiosInstance => {
  if (!apiClient) {
    return initializeApiClient()
  }
  return apiClient
}

// API Methods
export const apiMethods = {
  // Authentication
  login: async (email: string, password: string) => {
    const response = await getApiClient().post<APIResponse<{ access_token: string }>>(
      '/auth/login',
      { email, password }
    )
    return response.data
  },

  logout: async () => {
    await getApiClient().post('/auth/logout')
  },

  register: async (username: string, email: string, password: string) => {
    const response = await getApiClient().post<APIResponse<{ user_id: string }>>(
      '/auth/register',
      { username, email, password }
    )
    return response.data
  },

  // Documents
  uploadDocument: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await getApiClient().post<APIResponse<{ document_id: string; filename: string }>>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getDocuments: async (skip: number = 0, limit: number = 20) => {
    const response = await getApiClient().get<APIResponse<{ documents: any[]; total: number }>>(
      '/documents',
      {
        params: { skip, limit },
      }
    )
    return response.data
  },

  getDocument: async (documentId: string) => {
    const response = await getApiClient().get<APIResponse<any>>(
      `/documents/${documentId}`
    )
    return response.data
  },

  deleteDocument: async (documentId: string) => {
    const response = await getApiClient().delete<APIResponse<{ success: boolean }>>(
      `/documents/${documentId}`
    )
    return response.data
  },

  // Analysis
  analyzeDocument: async (documentId: string, techniques: string[]) => {
    const response = await getApiClient().post<APIResponse<{ analysis_id: string }>>(
      `/documents/${documentId}/analyze`,
      { techniques }
    )
    return response.data
  },

  getAnalysisResults: async (documentId: string) => {
    const response = await getApiClient().get<APIResponse<any>>(
      `/documents/${documentId}/analysis`
    )
    return response.data
  },

  getAnalysisStatus: async (analysisId: string) => {
    const response = await getApiClient().get<APIResponse<{ status: string; progress: number }>>(
      `/analysis/${analysisId}/status`
    )
    return response.data
  },

  // User
  getUserProfile: async () => {
    const response = await getApiClient().get<APIResponse<any>>(
      '/user/profile'
    )
    return response.data
  },

  updateUserProfile: async (data: Record<string, unknown>) => {
    const response = await getApiClient().put<APIResponse<any>>(
      '/user/profile',
      data
    )
    return response.data
  },

  getUserStats: async () => {
    const response = await getApiClient().get<APIResponse<any>>(
      '/user/stats'
    )
    return response.data
  },

  // Leaderboard
  getLeaderboard: async (limit: number = 100) => {
    const response = await getApiClient().get<APIResponse<any>>(
      '/leaderboard',
      {
        params: { limit },
      }
    )
    return response.data
  },

  // Health check
  healthCheck: async () => {
    const response = await getApiClient().get<APIResponse<{ status: string }>>(
      '/health'
    )
    return response.data
  },

  // WebSocket streaming analysis
  streamAnalysis: (
    documentId: string,
    techniques: string[],
    onMessage: (data: any) => void,
    onError: (error: string) => void,
    onComplete: () => void
  ) => {
    const apiUrl = useAppStore.getState().apiUrl
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws'
    const wsUrl = apiUrl.replace(/^https?/, wsProtocol).replace(/\/$/, '')
    
    const ws = new WebSocket(`${wsUrl}/ws/analyze`)
    
    ws.onopen = () => {
      ws.send(JSON.stringify({
        document_id: documentId,
        techniques: techniques,
        analysis_id: `${documentId}_${Date.now()}`,
      }))
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
        
        if (data.type === 'complete' || data.type === 'error') {
          onComplete()
        }
      } catch (e) {
        onError(`Failed to parse message: ${String(e)}`)
      }
    }
    
    ws.onerror = () => {
      onError('WebSocket connection error')
    }
    
    ws.onclose = () => {
      // Connection closed
    }
    
    // Return a function to close the connection
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  },
}

// Helper to handle API errors
export const handleApiError = (
  error: unknown
): { code: string; message: string; details?: Record<string, unknown> } => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as any
    if (apiError?.error) {
      return {
        code: apiError.error.code || 'API_ERROR',
        message: apiError.error.message || 'An error occurred',
        details: apiError.error.details,
      }
    }
    return {
      code: error.code || 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
    }
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
  }
}
