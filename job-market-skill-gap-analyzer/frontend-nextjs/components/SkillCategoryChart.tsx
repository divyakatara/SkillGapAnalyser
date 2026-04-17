'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface SkillData {
  skill: string
  job_count: number
  percentage: number
  category: string
  demand_level: string
}

interface Props {
  skills: SkillData[]
}

const COLORS = [
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
]

export default function SkillCategoryChart({ skills }: Props) {
  // Group skills by category
  const categoryData = skills.reduce((acc, skill) => {
    const existing = acc.find(item => item.name === skill.category)
    if (existing) {
      existing.value += 1
    } else {
      acc.push({ name: skill.category, value: 1 })
    }
    return acc
  }, [] as { name: string; value: number }[])

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Category Distribution
      </h2>
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={categoryData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {categoryData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {categoryData.map((category, index) => (
          <div key={category.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div 
                className="w-4 h-4 rounded"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              ></div>
              <span className="text-gray-700">{category.name}</span>
            </div>
            <span className="font-semibold text-gray-900">{category.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
