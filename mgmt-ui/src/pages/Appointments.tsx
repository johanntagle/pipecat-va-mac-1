import { useAppointments } from '../hooks/useAppointments'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import { format } from 'date-fns'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, User, Phone as PhoneIcon, Building2, Clock } from 'lucide-react'

export default function Appointments() {
  const { data: appointments, isLoading, error } = useAppointments()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} />
  if (!appointments || appointments.length === 0) {
    return <EmptyState title="No appointments" message="No appointments have been scheduled yet." />
  }

  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" => {
    switch (status) {
      case 'confirmed':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'cancelled':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">Appointments</h1>
        <p className="text-gray-500 mt-2">
          Manage scheduled appointments from voice agent calls
        </p>
        <div className="mt-4">
          <Badge variant="secondary" className="text-base px-4 py-1.5">
            {appointments.length} {appointments.length === 1 ? 'Appointment' : 'Appointments'}
          </Badge>
        </div>
      </div>

      {/* Appointments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {appointments.map((appointment) => (
          <Card key={appointment.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="bg-purple-50 p-2 rounded-lg">
                    <Calendar className="h-5 w-5 text-purple-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="truncate">{appointment.caller_name}</CardTitle>
                    <CardDescription>ID: {appointment.id}</CardDescription>
                  </div>
                </div>
                <Badge
                  variant={getStatusVariant(appointment.status)}
                  className={appointment.status === 'confirmed' ? 'bg-green-600 hover:bg-green-700' : ''}
                >
                  {appointment.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Company */}
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Company</p>
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-gray-400" />
                  <p className="text-sm font-medium text-gray-900">
                    {appointment.companies?.name || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Phone */}
              {appointment.caller_phone && (
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Phone</p>
                  <div className="flex items-center gap-2">
                    <PhoneIcon className="h-4 w-4 text-gray-400" />
                    <p className="text-sm text-gray-900 font-mono">
                      {appointment.caller_phone}
                    </p>
                  </div>
                </div>
              )}

              {/* Appointment Time */}
              <div className="pt-4 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Scheduled For</p>
                <div className="flex items-start gap-2">
                  <Clock className="h-4 w-4 text-purple-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      {format(new Date(appointment.appointment_time), 'EEEE, MMM d, yyyy')}
                    </p>
                    <p className="text-sm text-gray-600">
                      {format(new Date(appointment.appointment_time), 'h:mm a')}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

