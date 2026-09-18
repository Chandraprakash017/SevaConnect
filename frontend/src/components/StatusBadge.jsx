/**
 * StatusBadge — displays booking status as a colored pill with icon.
 */
import { Clock, Truck, Search, HelpCircle, Wrench, CheckCircle, XCircle, UserCheck } from 'lucide-react'

const STATUS_CONFIG = {
  requested:         { label: 'Requested',         badge: 'badge-blue',   icon: Clock },
  assigned:          { label: 'Assigned',           badge: 'badge-purple', icon: UserCheck },
  on_way:            { label: 'On the Way',         badge: 'badge-cyan',   icon: Truck },
  inspection:        { label: 'Inspecting',         badge: 'badge-yellow', icon: Search },
  waiting_approval:  { label: 'Awaiting Approval',  badge: 'badge-yellow', icon: HelpCircle },
  in_progress:       { label: 'In Progress',        badge: 'badge-blue',   icon: Wrench },
  completed:         { label: 'Completed',          badge: 'badge-green',  icon: CheckCircle },
  cancelled:         { label: 'Cancelled',          badge: 'badge-red',    icon: XCircle },
}

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, badge: 'badge-blue', icon: Clock }
  const Icon = config.icon

  return (
    <span className={`badge ${config.badge}`}>
      <Icon size={13} />
      {config.label}
    </span>
  )
}
