'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

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

const COLORS = {
  'High': '#ef4444',
  'Medium': '#f59e0b',
  'Low': '#10b981',
}

export default function SkillDemandChart({ skills }: Props) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Skills in Demand (Top {skills.length})
      </h2>
      <ResponsiveContainer width="100%" height={600}>
        <BarChart
          data={skills}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 100]} label={{ value: 'Percentage (%)', position: 'bottom' }} />
          <YAxis dataKey="skill" type="category" width={90} />
          <Tooltip 
            formatter={(value: number) => `${value.toFixed(1)}%`}
            labelStyle={{ color: '#000' }}
          />
          <Legend />
          <Bar dataKey="percentage" name="Job Percentage" radius={[0, 8, 8, 0]}>
            {skills.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.demand_level as keyof typeof COLORS] || '#3b82f6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
