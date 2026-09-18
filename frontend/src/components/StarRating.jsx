/**
 * StarRating — interactive star rating component.
 * Can be read-only (for display) or interactive (for review form).
 */
import { Star } from 'lucide-react'
import { useState } from 'react'

export default function StarRating({ rating = 0, onRate, size = 20, readonly = false }) {
  const [hover, setHover] = useState(0)

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = star <= (hover || rating)
        return (
          <button
            key={star}
            type="button"
            disabled={readonly}
            onClick={() => onRate?.(star)}
            onMouseEnter={() => !readonly && setHover(star)}
            onMouseLeave={() => !readonly && setHover(0)}
            className={`transition-all duration-200 ${
              readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'
            }`}
            style={{ background: 'none', border: 'none', padding: '2px' }}
          >
            <Star
              size={size}
              fill={filled ? '#fbbf24' : 'transparent'}
              color={filled ? '#fbbf24' : '#4b5563'}
              strokeWidth={1.5}
            />
          </button>
        )
      })}
    </div>
  )
}
