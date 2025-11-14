import { useQuery } from '@tanstack/react-query'
import { supabase } from '../lib/supabase'

export function useCalls() {
  return useQuery({
    queryKey: ['calls'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('calls')
        .select(`
          *,
          companies (
            id,
            name
          )
        `)
        .order('start_time', { ascending: false })

      if (error) throw error
      return data
    },
  })
}

export function useCallDetails(callId: number) {
  return useQuery({
    queryKey: ['call-details', callId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('call_details')
        .select('*')
        .eq('call_id', callId)
        .order('timestamp', { ascending: true })

      if (error) throw error
      return data
    },
    enabled: !!callId,
  })
}

