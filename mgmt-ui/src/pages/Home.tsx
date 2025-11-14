import { Link } from 'react-router-dom'
import { useCompanies } from '../hooks/useCompanies'
import { useCalls } from '../hooks/useCalls'
import { useAppointments } from '../hooks/useAppointments'
import { useDocuments } from '../hooks/useDocuments'
import { useRagChunks } from '../hooks/useRagChunks'
import { format } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Building2, Phone, Calendar, FileText, Puzzle, ArrowRight, Clock } from 'lucide-react'

export default function Home() {
  const { data: companies } = useCompanies()
  const { data: calls } = useCalls()
  const { data: appointments } = useAppointments()
  const { data: documents } = useDocuments()
  const { data: ragChunks } = useRagChunks()

  const stats = [
    { 
      name: 'Companies', 
      value: companies?.length || 0, 
      href: '/companies', 
      icon: Building2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    { 
      name: 'Calls', 
      value: calls?.length || 0, 
      href: '/calls', 
      icon: Phone,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    { 
      name: 'Appointments', 
      value: appointments?.length || 0, 
      href: '/appointments', 
      icon: Calendar,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    { 
      name: 'Documents', 
      value: documents?.length || 0, 
      href: '/documents', 
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    { 
      name: 'RAG Chunks', 
      value: ragChunks?.length || 0, 
      href: '/rag-chunks', 
      icon: Puzzle,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50'
    },
  ]

  const recentCalls = calls?.slice(0, 5) || []

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-gray-500 mt-2">
          Monitor and manage your voice agent system
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link key={stat.name} to={stat.href}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.name}
                  </CardTitle>
                  <div className={`${stat.bgColor} p-2 rounded-lg`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    Total {stat.name.toLowerCase()}
                  </p>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
            <CardDescription>Latest voice agent interactions</CardDescription>
          </CardHeader>
          <CardContent>
            {recentCalls.length > 0 ? (
              <div className="space-y-3">
                {recentCalls.map((call) => (
                  <div
                    key={call.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="bg-green-50 p-2 rounded-lg">
                        <Phone className="h-4 w-4 text-green-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{call.companies?.name || 'Unknown'}</p>
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Clock className="h-3 w-3" />
                          <span>{format(new Date(call.start_time), 'MMM d, h:mm a')}</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      {call.duration_seconds ? (
                        <Badge variant="secondary">
                          {call.duration_seconds}s
                        </Badge>
                      ) : (
                        <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
                          Live
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No calls yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Navigate to key sections</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {stats.map((stat) => {
                const Icon = stat.icon
                return (
                  <Link
                    key={stat.name}
                    to={stat.href}
                    className="group p-4 rounded-lg border hover:border-blue-500 hover:shadow-md transition-all"
                  >
                    <div className={`${stat.bgColor} p-2 rounded-lg w-fit mb-2`}>
                      <Icon className={`h-5 w-5 ${stat.color}`} />
                    </div>
                    <div className="font-medium text-sm">{stat.name}</div>
                    <div className="flex items-center gap-1 text-xs text-gray-500 mt-1 group-hover:text-blue-600 transition-colors">
                      <span>View all</span>
                      <ArrowRight className="h-3 w-3" />
                    </div>
                  </Link>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
