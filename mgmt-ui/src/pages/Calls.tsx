import { useState } from 'react'
import { useCalls } from '../hooks/useCalls'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import CallDetailsModal from '../components/CallDetailsModal'
import { format } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Phone, Clock, Calendar, ArrowRight, Building2 } from 'lucide-react'

export default function Calls() {
  const { data: calls, isLoading, error } = useCalls()
  const [selectedCallId, setSelectedCallId] = useState<number | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleViewDetails = (callId: number) => {
    setSelectedCallId(callId)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedCallId(null)
  }

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} />
  if (!calls || calls.length === 0) {
    return <EmptyState title="No calls" message="No calls have been recorded yet." />
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Call History</h1>
        <p className="text-gray-500 mt-2">
          View and manage all voice agent calls
        </p>
        <div className="mt-4">
          <Badge variant="secondary" className="text-base px-4 py-1.5">
            {calls.length} {calls.length === 1 ? 'Call' : 'Calls'}
          </Badge>
        </div>
      </div>

      {/* Calls List */}
      <div className="space-y-4">
        {calls.map((call) => (
          <Card key={call.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="bg-green-50 p-2 rounded-lg">
                    <Phone className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="truncate">
                      {call.companies?.name || 'Unknown Company'}
                    </CardTitle>
                    <p className="text-sm text-gray-500">Call ID: {call.id}</p>
                  </div>
                </div>
                <Button onClick={() => handleViewDetails(call.id)}>
                  View Details
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Call Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Start Time */}
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Start Time</p>
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">
                        {format(new Date(call.start_time), 'MMM d, yyyy')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {format(new Date(call.start_time), 'h:mm:ss a')}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Duration</p>
                  {call.duration_seconds ? (
                    <Badge variant="default" className="bg-green-600 hover:bg-green-700">
                      <Clock className="h-3 w-3 mr-1" />
                      {call.duration_seconds}s
                    </Badge>
                  ) : (
                    <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
                      <Clock className="h-3 w-3 mr-1 animate-pulse" />
                      Live
                    </Badge>
                  )}
                </div>

                {/* End Time */}
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">End Time</p>
                  {call.end_time ? (
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="font-medium text-gray-900">
                          {format(new Date(call.end_time), 'MMM d, yyyy')}
                        </p>
                        <p className="text-xs text-gray-500">
                          {format(new Date(call.end_time), 'h:mm:ss a')}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 italic">Ongoing</p>
                  )}
                </div>
              </div>

              {/* Summary */}
              {call.summary && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Summary</p>
                  <p className="text-sm text-gray-700">{call.summary}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <CallDetailsModal
        callId={selectedCallId}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  )
}

