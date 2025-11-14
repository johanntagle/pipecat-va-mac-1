import { useCompanies } from '../hooks/useCompanies'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import { format } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Building2, CheckCircle2, XCircle, Calendar } from 'lucide-react'

export default function Companies() {
  const { data: companies, isLoading, error } = useCompanies()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} />
  if (!companies || companies.length === 0) {
    return <EmptyState title="No companies" message="No companies have been created yet." />
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Companies</h1>
        <p className="text-gray-500 mt-2">
          Manage and view all companies in your system
        </p>
        <div className="mt-4">
          <Badge variant="secondary" className="text-base px-4 py-1.5">
            {companies.length} {companies.length === 1 ? 'Company' : 'Companies'}
          </Badge>
        </div>
      </div>

      {/* Companies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map((company) => (
          <Card key={company.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="bg-blue-50 p-2 rounded-lg">
                    <Building2 className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="truncate">{company.name}</CardTitle>
                    <CardDescription>ID: {company.id}</CardDescription>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* LLM Model */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">LLM Model</p>
                <p className="text-sm font-medium text-gray-900">
                  {company.llm_model || (
                    <span className="text-gray-400 italic">Not configured</span>
                  )}
                </p>
              </div>

              {/* API Key Status */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">API Key</p>
                {company.openai_api_key ? (
                  <Badge variant="default" className="bg-green-600 hover:bg-green-700">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Configured
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <XCircle className="h-3 w-3 mr-1" />
                    Not Set
                  </Badge>
                )}
              </div>

              {/* Created Date */}
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Calendar className="h-3 w-3" />
                  <span>Created {format(new Date(company.created_at), 'MMM d, yyyy')}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

