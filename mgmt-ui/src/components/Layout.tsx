import { Outlet, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { LayoutDashboard, Building2, Phone, Calendar, FileText, Puzzle, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Companies', href: '/companies', icon: Building2 },
  { name: 'Calls', href: '/calls', icon: Phone },
  { name: 'Appointments', href: '/appointments', icon: Calendar },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'RAG Chunks', href: '/rag-chunks', icon: Puzzle },
]

export default function Layout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? 'w-64' : 'w-20'
          } bg-white border-r border-gray-200 transition-all duration-300 flex flex-col`}
        >
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            {sidebarOpen ? (
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  Call Manager
                </h2>
                <p className="text-xs text-gray-500 mt-1">Voice Agent System</p>
              </div>
            ) : (
              <Phone className="h-6 w-6 text-blue-600" />
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="h-8 w-8"
            >
              {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  } group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    sidebarOpen ? '' : 'justify-center'
                  }`}
                  title={!sidebarOpen ? item.name : ''}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {sidebarOpen && <span className="ml-3">{item.name}</span>}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            {sidebarOpen ? (
              <div className="text-xs text-gray-500">
                <p>© {new Date().getFullYear()} Call Manager</p>
                <p className="mt-1">v1.0.0</p>
              </div>
            ) : (
              <div className="text-center text-gray-400">
                <div className="h-2 w-2 bg-green-500 rounded-full mx-auto"></div>
              </div>
            )}
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

