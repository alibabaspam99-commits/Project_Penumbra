/**
 * Core type definitions for Penumbra frontend
 */

// User and Authentication
export interface User {
  id: string
  username: string
  email: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface AuthToken {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// PDF and Document Analysis
export interface PDFDocument {
  id: string
  filename: string
  size: number
  pages: number
  upload_date: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error?: string
}

export interface Page {
  number: number
  width: number
  height: number
  image_url?: string
  has_text_layer: boolean
  redactions: RedactionResult[]
}

export interface RedactionResult {
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

// Recovery Techniques
export interface TechniqueResult {
  technique_name: string
  success: boolean
  data: Record<string, unknown>
  timestamp: string
}

export interface TextExtractionResult {
  text: string
  confidence: number
}

export interface EdgeAnalysisResult {
  edge_pixels: number[][]
  gradient_data: number[][]
  detected_characters: string[]
}

// Analysis Results
export interface AnalysisResult {
  id: string
  document_id: string
  user_id: string
  started_at: string
  completed_at?: string
  results: {
    ocg_layers?: TechniqueResult
    text_extraction?: TechniqueResult
    edge_analysis?: TechniqueResult
    over_redaction?: TechniqueResult
    width_filter?: TechniqueResult
  }
  verified_count: number
  total_count: number
}

// Gamification and User Stats
export interface UserStats {
  user_id: string
  total_pdfs_processed: number
  total_redactions_analyzed: number
  verified_count: number
  accuracy: number
  current_streak: number
  best_streak: number
  total_points: number
  level: number
  rank: string
}

export interface Achievement {
  id: string
  name: string
  description: string
  icon_url: string
  earned_at: string
}

export interface Leaderboard {
  rank: number
  user_id: string
  username: string
  avatar_url?: string
  points: number
  pdfs_processed: number
  accuracy: number
}

// UI State Management
export interface UIState {
  currentTab: 'upload' | 'analyze' | 'results' | 'profile' | 'leaderboard' | 'settings'
  selectedDocument?: PDFDocument
  selectedPage?: number
  zoomLevel: number
  isDarkMode: boolean
  isMobileMenuOpen: boolean
}

export interface UploadState {
  files: File[]
  isUploading: boolean
  uploadProgress: number
  error?: string
}

export interface AnalysisState {
  isProcessing: boolean
  currentStep: string
  progress: number
  results?: AnalysisResult
  error?: string
}

// WebSocket Messages
export interface WSMessage {
  type: string
  payload: Record<string, unknown>
}

export interface ProcessingUpdate {
  document_id: string
  status: 'processing' | 'completed' | 'error'
  progress: number
  message: string
}

// API Response Wrapper
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
  timestamp: string
}

// Batch Operations
export interface BatchOperation {
  id: string
  name: string
  documents: PDFDocument[]
  status: 'pending' | 'processing' | 'completed'
  progress: number
  created_at: string
  completed_at?: string
}
