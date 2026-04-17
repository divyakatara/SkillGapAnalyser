'use client'

import Link from 'next/link'
import { BarChart3, FileText, Upload } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2">
            <BarChart3 className="w-8 h-8 text-primary" />
            <span className="text-xl font-bold text-gray-800">
              Job Market Analyzer
            </span>
          </Link>
          
          <div className="flex space-x-4">
            <Link
              href="/"
              className="flex items-center space-x-1 px-4 py-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              <BarChart3 className="w-5 h-5" />
              <span>Market Overview</span>
            </Link>
            <Link
              href="/gap-analysis"
              className="flex items-center space-x-1 px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              <Upload className="w-5 h-5" />
              <span>Upload Resume</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
