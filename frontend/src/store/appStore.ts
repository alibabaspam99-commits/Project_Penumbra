import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type {
  UIState,
  PDFDocument,
  AnalysisResult,
  User,
  UserStats,
} from '../types'

export interface AppState {
  // UI State
  uiState: UIState
  setCurrentTab: (tab: UIState['currentTab']) => void
  setZoomLevel: (level: number) => void
  setDarkMode: (isDark: boolean) => void
  setMobileMenuOpen: (open: boolean) => void

  // User State
  user: User | null
  isAuthenticated: boolean
  userStats: UserStats | null
  setUser: (user: User | null) => void
  setUserStats: (stats: UserStats | null) => void
  logout: () => void

  // Document State
  documents: PDFDocument[]
  selectedDocument: PDFDocument | null
  isLoadingDocuments: boolean
  documentError: string | null
  setDocuments: (docs: PDFDocument[]) => void
  setSelectedDocument: (doc: PDFDocument | null) => void
  addDocument: (doc: PDFDocument) => void
  removeDocument: (id: string) => void
  updateDocumentStatus: (id: string, status: PDFDocument['status']) => void
  setLoadingDocuments: (loading: boolean) => void
  setDocumentError: (error: string | null) => void

  // Analysis State
  currentAnalysis: AnalysisResult | null
  analysisHistory: AnalysisResult[]
  isAnalyzing: boolean
  analysisProgress: number
  analysisError: string | null
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void
  addAnalysisToHistory: (analysis: AnalysisResult) => void
  setIsAnalyzing: (analyzing: boolean) => void
  setAnalysisProgress: (progress: number) => void
  setAnalysisError: (error: string | null) => void
  clearAnalysisHistory: () => void

  // API Configuration
  apiUrl: string
  wsUrl: string
  setApiUrl: (url: string) => void
  setWsUrl: (url: string) => void

  // Notifications
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'info' | 'warning'
    message: string
    timestamp: number
  }>
  addNotification: (
    type: 'success' | 'error' | 'info' | 'warning',
    message: string
  ) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // Reset
  resetAppState: () => void
}

const initialUIState: UIState = {
  currentTab: 'upload',
  zoomLevel: 100,
  isDarkMode: false,
  isMobileMenuOpen: false,
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // UI State
        uiState: initialUIState,
        setCurrentTab: (tab) =>
          set((state) => ({
            uiState: { ...state.uiState, currentTab: tab },
          })),
        setZoomLevel: (level) =>
          set((state) => ({
            uiState: { ...state.uiState, zoomLevel: Math.max(50, Math.min(200, level)) },
          })),
        setDarkMode: (isDark) =>
          set((state) => ({
            uiState: { ...state.uiState, isDarkMode: isDark },
          })),
        setMobileMenuOpen: (open) =>
          set((state) => ({
            uiState: { ...state.uiState, isMobileMenuOpen: open },
          })),

        // User State
        user: null,
        isAuthenticated: false,
        userStats: null,
        setUser: (user) =>
          set({
            user,
            isAuthenticated: user !== null,
          }),
        setUserStats: (stats) => set({ userStats: stats }),
        logout: () =>
          set({
            user: null,
            isAuthenticated: false,
            userStats: null,
          }),

        // Document State
        documents: [],
        selectedDocument: null,
        isLoadingDocuments: false,
        documentError: null,
        setDocuments: (docs) => set({ documents: docs }),
        setSelectedDocument: (doc) => set({ selectedDocument: doc }),
        addDocument: (doc) =>
          set((state) => ({
            documents: [doc, ...state.documents],
          })),
        removeDocument: (id) =>
          set((state) => ({
            documents: state.documents.filter((d) => d.id !== id),
          })),
        updateDocumentStatus: (id, status) =>
          set((state) => ({
            documents: state.documents.map((d) =>
              d.id === id ? { ...d, status } : d
            ),
            selectedDocument:
              state.selectedDocument?.id === id
                ? { ...state.selectedDocument, status }
                : state.selectedDocument,
          })),
        setLoadingDocuments: (loading) => set({ isLoadingDocuments: loading }),
        setDocumentError: (error) => set({ documentError: error }),

        // Analysis State
        currentAnalysis: null,
        analysisHistory: [],
        isAnalyzing: false,
        analysisProgress: 0,
        analysisError: null,
        setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
        addAnalysisToHistory: (analysis) =>
          set((state) => ({
            analysisHistory: [analysis, ...state.analysisHistory].slice(0, 50),
          })),
        setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
        setAnalysisProgress: (progress) =>
          set({ analysisProgress: Math.max(0, Math.min(100, progress)) }),
        setAnalysisError: (error) => set({ analysisError: error }),
        clearAnalysisHistory: () => set({ analysisHistory: [] }),

        // API Configuration
        apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
        wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
        setApiUrl: (url) => set({ apiUrl: url }),
        setWsUrl: (url) => set({ wsUrl: url }),

        // Notifications
        notifications: [],
        addNotification: (type, message) =>
          set((state) => ({
            notifications: [
              ...state.notifications,
              {
                id: `${Date.now()}-${Math.random()}`,
                type,
                message,
                timestamp: Date.now(),
              },
            ],
          })),
        removeNotification: (id) =>
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          })),
        clearNotifications: () => set({ notifications: [] }),

        // Reset
        resetAppState: () =>
          set({
            uiState: initialUIState,
            user: null,
            isAuthenticated: false,
            userStats: null,
            documents: [],
            selectedDocument: null,
            isLoadingDocuments: false,
            documentError: null,
            currentAnalysis: null,
            analysisHistory: [],
            isAnalyzing: false,
            analysisProgress: 0,
            analysisError: null,
            notifications: [],
          }),
      }),
      {
        name: 'penumbra-store',
        partialize: (state) => ({
          uiState: state.uiState,
          user: state.user,
          documents: state.documents,
          analysisHistory: state.analysisHistory,
        }),
      }
    ),
    { name: 'AppStore' }
  )
)
