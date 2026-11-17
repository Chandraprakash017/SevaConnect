import { useEffect, useRef, useState } from 'react'
import { Clock, MapPin, TriangleAlert } from 'lucide-react'

let mapsPromise

function loadGoogleMaps(apiKey) {
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (!apiKey) return Promise.reject(new Error('Add VITE_GOOGLE_MAPS_API_KEY to the frontend environment to enable the live map.'))
  if (mapsPromise) return mapsPromise

  mapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&v=weekly`
    script.async = true
    script.defer = true
    script.onload = () => {
      if (window.google?.maps) {
        resolve(window.google.maps)
      } else {
        mapsPromise = null
        reject(new Error('Google Maps did not initialize. Check that the Maps JavaScript API is enabled for this key.'))
      }
    }
    script.onerror = () => {
      mapsPromise = null
      reject(new Error('Google Maps could not be loaded. Check the network connection and API key restrictions.'))
    }
    document.head.appendChild(script)
  })

  return mapsPromise
}

function toLatLng(location) {
  if (!location) return null
  const latitude = Number(location.latitude)
  const longitude = Number(location.longitude)
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null
  return { lat: latitude, lng: longitude }
}

export default function LiveTrackingMap({ destination, technicianLocation, onEtaChange }) {
  const mapElement = useRef(null)
  const map = useRef(null)
  const technicianMarker = useRef(null)
  const destinationMarker = useRef(null)
  const directionsService = useRef(null)
  const directionsRenderer = useRef(null)
  const lastRouteRequestAt = useRef(0)
  const [mapReady, setMapReady] = useState(false)
  const [mapError, setMapError] = useState('')
  const [routeError, setRouteError] = useState('')

  const destinationLatLng = toLatLng(destination)
  const technicianLatLng = toLatLng(technicianLocation)
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

  useEffect(() => {
    let active = true
    loadGoogleMaps(apiKey)
      .then((maps) => {
        if (!active || !mapElement.current) return
        map.current = new maps.Map(mapElement.current, {
          center: destinationLatLng || { lat: 20.5937, lng: 78.9629 },
          zoom: destinationLatLng ? 14 : 5,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: true,
        })
        directionsService.current = new maps.DirectionsService()
        directionsRenderer.current = new maps.DirectionsRenderer({
          map: map.current,
          suppressMarkers: true,
          preserveViewport: false,
          polylineOptions: { strokeColor: '#3b82f6', strokeOpacity: 0.85, strokeWeight: 5 },
        })
        setMapReady(true)
      })
      .catch((error) => {
        if (active) setMapError(error.message)
      })

    return () => { active = false }
  }, [apiKey])

  useEffect(() => {
    if (!mapReady || !window.google?.maps) return
    const maps = window.google.maps

    if (destinationLatLng) {
      if (!destinationMarker.current) {
        destinationMarker.current = new maps.Marker({
          map: map.current,
          position: destinationLatLng,
          label: { text: 'You', color: '#ffffff', fontWeight: '700' },
          title: 'Your service location',
        })
      } else {
        destinationMarker.current.setPosition(destinationLatLng)
      }
      if (!technicianLatLng) map.current.setCenter(destinationLatLng)
    }

    if (technicianLatLng) {
      if (!technicianMarker.current) {
        technicianMarker.current = new maps.Marker({
          map: map.current,
          position: technicianLatLng,
          label: { text: 'T', color: '#ffffff', fontWeight: '700' },
          title: 'Technician location',
        })
      } else {
        technicianMarker.current.setPosition(technicianLatLng)
      }

      const now = Date.now()
      if (destinationLatLng && now - lastRouteRequestAt.current >= 60000) {
        lastRouteRequestAt.current = now
        setRouteError('')
        onEtaChange(null)
        directionsRenderer.current.setMap(null)
        directionsService.current.route({
          origin: technicianLatLng,
          destination: destinationLatLng,
          travelMode: maps.TravelMode.DRIVING,
          drivingOptions: {
            departureTime: new Date(),
            trafficModel: 'bestguess',
          },
        }, (result, status) => {
          if (status !== 'OK' || !result?.routes?.[0]?.legs?.[0]) {
            setRouteError(`Route unavailable (${status}). Check that the Routes/Directions service is enabled for the Maps key.`)
            onEtaChange(null)
            return
          }

          directionsRenderer.current.setMap(map.current)
          directionsRenderer.current.setDirections(result)
          const leg = result.routes[0].legs[0]
          const durationSeconds = leg.duration_in_traffic?.value ?? leg.duration?.value
          if (Number.isFinite(durationSeconds)) {
            const arrival = new Date(Date.now() + durationSeconds * 1000)
            onEtaChange({
              minutes: Math.max(1, Math.round(durationSeconds / 60)),
              arrivalTime: arrival.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
              arrivalTimestamp: arrival.getTime(),
            })
          }
        })
      } else if (!destinationLatLng) {
        map.current.setCenter(technicianLatLng)
      }
    } else {
      technicianMarker.current?.setMap(null)
      technicianMarker.current = null
      directionsRenderer.current?.setMap(null)
      onEtaChange(null)
      if (destinationLatLng) map.current.setCenter(destinationLatLng)
    }
  }, [destinationLatLng?.lat, destinationLatLng?.lng, technicianLatLng?.lat, technicianLatLng?.lng, mapReady, onEtaChange])

  return (
    <div>
      <div className="relative overflow-hidden rounded-xl border border-white/10">
        <div ref={mapElement} className="h-72 w-full bg-slate-900" aria-label="Live technician tracking map" />
        {mapError && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/90 p-6 text-center">
            <div className="max-w-md">
              <TriangleAlert className="mx-auto mb-2 text-amber-400" size={22} />
              <p className="text-sm text-amber-200">{mapError}</p>
            </div>
          </div>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 pt-3 text-xs" style={{ color: 'var(--text-muted)' }}>
        <span className="flex items-center gap-1.5"><span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-[10px] font-bold text-white">T</span> Technician</span>
        <span className="flex items-center gap-1.5"><MapPin size={14} className="text-rose-400" /> Your location</span>
        {routeError && <span className="flex items-center gap-1.5 text-amber-300"><Clock size={13} /> {routeError}</span>}
      </div>
    </div>
  )
}
