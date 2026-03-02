import React, { useState, useCallback } from 'react'
import './SearchBar.css'

interface SearchBarProps {
  placeholder?: string
  onSearch: (query: string) => void
  onClear?: () => void
  debounceMs?: number
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search...',
  onSearch,
  onClear,
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const debounceTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value
      setQuery(value)

      // Clear existing timer
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }

      // Set new timer
      debounceTimer.current = setTimeout(() => {
        onSearch(value)
      }, debounceMs)
    },
    [onSearch, debounceMs]
  )

  const handleClear = useCallback(() => {
    setQuery('')
    onClear?.()
    onSearch('')
  }, [onSearch, onClear])

  return (
    <div className={`search-bar ${isFocused ? 'focused' : ''}`}>
      <span className="search-icon">🔍</span>
      <input
        type="text"
        className="search-input"
        placeholder={placeholder}
        value={query}
        onChange={handleChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
      {query && (
        <button
          className="search-clear"
          onClick={handleClear}
          aria-label="Clear search"
          type="button"
        >
          ✕
        </button>
      )}
    </div>
  )
}

interface FilterBarProps {
  filters: Array<{
    label: string
    value: string
    options: Array<{ label: string; value: string }>
  }>
  onFilterChange: (filterName: string, value: string) => void
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onFilterChange }) => {
  return (
    <div className="filter-bar">
      {filters.map((filter) => (
        <div key={filter.value} className="filter-group">
          <label className="filter-label">{filter.label}</label>
          <select
            className="filter-select"
            onChange={(e) => onFilterChange(filter.value, e.target.value)}
            defaultValue=""
          >
            <option value="">All</option>
            {filter.options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  )
}
