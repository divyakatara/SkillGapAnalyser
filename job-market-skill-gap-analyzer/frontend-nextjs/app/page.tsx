'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import SkillDemandChart from '@/components/SkillDemandChart'
import SkillCategoryChart from '@/components/SkillCategoryChart'
import StatsCard from '@/components/StatsCard'
import SearchBar from '@/components/SearchBar'
import { TrendingUp, Briefcase, Award, Target } from 'lucide-react'

interface SkillData {
  skill: string
  job_count: number
  percentage: number
  category: string
  demand_level: string
}

export default function Home() {
  const [skills, setSkills] = useState<SkillData[]>([])
  const [filteredSkills, setFilteredSkills] = useState<SkillData[]>([])
  const [topN, setTopN] = useState(20)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalJobs: 0,
    uniqueSkills: 0,
    avgSkillsPerJob: 0,
    topSkill: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterSkills()
  }, [searchQuery, skills])

  const loadData = async () => {
    try {
      setLoading(true)
      // Load skill demand data
      const response = await axios.get('http://localhost:8000/api/skill-demand')
      const skillData = response.data.skills || []
      setSkills(skillData)
      setFilteredSkills(skillData)

      // Load job stats
      const statsResponse = await axios.get('http://localhost:8000/api/job-stats')
      setStats({
        totalJobs: statsResponse.data.total_jobs || 200,
        uniqueSkills: skillData.length,
        avgSkillsPerJob: statsResponse.data.avg_skills_per_job || 27.4,
        topSkill: skillData[0]?.skill || 'N/A'
      })
    } catch (error) {
      console.error('Error loading data:', error)
      // Load from local files as fallback
      loadLocalData()
    } finally {
      setLoading(false)
    }
  }

  const loadLocalData = async () => {
    try {
      const response = await fetch('/data/skill_demand.json')
      const data = await response.json()
      setSkills(data)
      setFilteredSkills(data)
      setStats({
        totalJobs: 200,
        uniqueSkills: data.length,
        avgSkillsPerJob: 27.4,
        topSkill: data[0]?.skill || 'N/A'
      })
    } catch (error) {
      console.error('Error loading local data:', error)
    }
  }

  const filterSkills = () => {
    if (!searchQuery.trim()) {
      setFilteredSkills(skills)
      return
    }

    const query = searchQuery.toLowerCase()
    const filtered = skills.filter(skill => 
      skill.skill.toLowerCase().includes(query) ||
      skill.category.toLowerCase().includes(query)
    )
    setFilteredSkills(filtered)
  }

  const displayedSkills = filteredSkills.slice(0, topN)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          📊 Job Market Skill Gap Analyzer
        </h1>
        <p className="text-gray-600">
          Discover in-demand skills and identify career development opportunities
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Jobs"
          value={stats.totalJobs.toLocaleString()}
          icon={<Briefcase className="w-8 h-8 text-blue-500" />}
          color="blue"
        />
        <StatsCard
          title="Unique Skills"
          value={stats.uniqueSkills.toString()}
          icon={<Award className="w-8 h-8 text-green-500" />}
          color="green"
        />
        <StatsCard
          title="Avg Skills/Job"
          value={stats.avgSkillsPerJob.toFixed(1)}
          icon={<Target className="w-8 h-8 text-purple-500" />}
          color="purple"
        />
        <StatsCard
          title="Top Skill"
          value={stats.topSkill}
          icon={<TrendingUp className="w-8 h-8 text-orange-500" />}
          color="orange"
        />
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search by skill name or category..."
            />
          </div>
          <div className="w-full md:w-64">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of skills to display
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={topN}
              onChange={(e) => setTopN(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>5</span>
              <span className="font-bold text-primary">{topN}</span>
              <span>50</span>
            </div>
          </div>
        </div>
        
        {searchQuery && (
          <div className="mt-4 text-sm text-gray-600">
            Found <span className="font-bold text-primary">{filteredSkills.length}</span> skills matching "{searchQuery}"
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="lg:col-span-2">
          <SkillDemandChart skills={displayedSkills} />
        </div>
        <div>
          <SkillCategoryChart skills={displayedSkills} />
        </div>
      </div>

      {/* Skill List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Top {displayedSkills.length} Skills in Demand
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Skill
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Jobs
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Demand
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {displayedSkills.map((skill, index) => (
                <tr key={skill.skill} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {index + 1}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                    {skill.skill}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                      {skill.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {skill.job_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {skill.percentage.toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      skill.demand_level === 'High' 
                        ? 'bg-red-100 text-red-800'
                        : skill.demand_level === 'Medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {skill.demand_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
