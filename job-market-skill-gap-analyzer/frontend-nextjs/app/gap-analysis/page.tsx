'use client'

import { useState } from 'react'
import { Upload, FileText, Check, X, AlertCircle } from 'lucide-react'

export default function GapAnalysis() {
  const [resume, setResume] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setResume(file)
    setAnalysis(null)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (!resume) return

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', resume)

    try {
      const response = await fetch('http://localhost:8000/api/upload-resume', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`Failed to analyze: ${response.statusText}`)
      }
      
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      console.error('Error analyzing resume:', error)
      setError(error instanceof Error ? error.message : 'Failed to analyze resume. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          🎯 Skill Gap Analysis
        </h1>
        <p className="text-gray-600">
          Upload your resume to discover missing skills and career opportunities
        </p>
      </div>

      {/* Upload Section */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className="w-12 h-12 text-gray-400 mb-3" />
              <p className="mb-2 text-sm text-gray-500">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500">PDF, DOCX, or TXT (MAX. 10MB)</p>
              {resume && (
                <div className="mt-4 flex items-center space-x-2 text-sm text-blue-600">
                  <FileText className="w-5 h-5" />
                  <span className="font-medium">{resume.name}</span>
                </div>
              )}
            </div>
            <input
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={handleFileSelect}
            />
          </label>
          
          {/* Analyze Button */}
          {resume && !loading && (
            <button
              onClick={handleAnalyze}
              className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
            >
              <Upload className="w-5 h-5" />
              <span>Analyze Resume</span>
            </button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-red-800">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Analyzing your resume...</p>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !loading && (
        <div className="space-y-8">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">{analysis.skill_count || 0}</div>
              <div className="text-sm text-gray-600 mt-1">Skills Found</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-green-600">{analysis.matched_skills?.length || 0}</div>
              <div className="text-sm text-gray-600 mt-1">Skills Matched</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-red-600">
                {(analysis.missing_high_demand?.length || 0) + (analysis.missing_medium_demand?.length || 0)}
              </div>
              <div className="text-sm text-gray-600 mt-1">Skills to Learn</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Skills You Have */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Check className="w-6 h-6 text-green-500" />
                <h2 className="text-2xl font-bold text-gray-800">
                  Skills You Have ({analysis.matched_skills?.length || 0})
                </h2>
              </div>
              {analysis.matched_skills && analysis.matched_skills.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {analysis.matched_skills.map((skill: string, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center p-3 bg-green-50 rounded-lg"
                    >
                      <Check className="w-4 h-4 text-green-600 mr-2 flex-shrink-0" />
                      <span className="font-medium text-gray-800">{skill}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No matched skills found</p>
              )}
            </div>

            {/* Skills You're Missing */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-2 mb-4">
                <X className="w-6 h-6 text-red-500" />
                <h2 className="text-2xl font-bold text-gray-800">
                  High-Priority Skills to Learn
                </h2>
              </div>
              {analysis.missing_high_demand && analysis.missing_high_demand.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {analysis.missing_high_demand.map((skill: string, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-red-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-800">{skill}</span>
                      <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                        High Demand
                      </span>
                    </div>
                  ))}
                  {analysis.missing_medium_demand?.slice(0, 5).map((skill: string, idx: number) => (
                    <div
                      key={`medium-${idx}`}
                      className="flex items-center justify-between p-3 bg-orange-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-800">{skill}</span>
                      <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                        Medium Demand
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">Great! You have all the high-demand skills</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
