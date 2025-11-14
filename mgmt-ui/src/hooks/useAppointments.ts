import { useQuery } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

export function useAppointments() {
  return useQuery({
    queryKey: ['appointments'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('appointments')
        .select(`
          *,
          companies (
            id,
            name
          ),
          calls (
            id,
            start_time
          )
        `)
        .order('appointment_time', { ascending: false })

      if (error) throw error
      return data
    },
  })
}

