import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { useCallDetails } from '../hooks/useCalls'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'
import EmptyState from './EmptyState'
import { format } from 'date-fns'

interface CallDetailsModalProps {
  callId: number | null
  isOpen: boolean
  onClose: () => void
}

export default function CallDetailsModal({ callId, isOpen, onClose }: CallDetailsModalProps) {
  const { data: details, isLoading, error } = useCallDetails(callId || 0)

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900 px-6 py-4 border-b border-gray-200"
                >
                  Call Details - Call #{callId}
                </Dialog.Title>

                <div className="px-6 py-4 max-h-[600px] overflow-y-auto">
                  {isLoading && <LoadingSpinner />}
                  
                  {error && <ErrorMessage message={error.message} />}
                  
                  {!isLoading && !error && (!details || details.length === 0) && (
                    <EmptyState 
                      title="No conversation details" 
                      message="No conversation details are available for this call." 
                    />
                  )}

                  {!isLoading && !error && details && details.length > 0 && (
                    <div className="space-y-4">
                      {details.map((detail) => (
                        <div
                          key={detail.id}
                          className={`flex ${
                            detail.speaker === 'agent' ? 'justify-start' : 'justify-end'
                          }`}
                        >
                          <div
                            className={`max-w-[75%] rounded-lg px-4 py-3 ${
                              detail.speaker === 'agent'
                                ? 'bg-blue-100 text-blue-900'
                                : 'bg-gray-100 text-gray-900'
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-semibold uppercase">
                                {detail.speaker}
                              </span>
                              <span className="text-xs text-gray-500">
                                {format(new Date(detail.timestamp), 'HH:mm:ss')}
                              </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap">{detail.message}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-transparent bg-blue-100 px-4 py-2 text-sm font-medium text-blue-900 hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                    onClick={onClose}
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}

