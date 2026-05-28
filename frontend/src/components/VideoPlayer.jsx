import { Play } from 'lucide-react'

export default function VideoPlayer({ src, title }) {
  if (!src) return null

  return (
    <div className="relative w-full bg-black rounded-xl overflow-hidden">
      <video
        src={src}
        controls
        controlsList="nodownload"
        className="w-full max-h-[70vh] object-contain"
        preload="metadata"
      >
        Seu navegador não suporta reprodução de vídeo.
      </video>
      {title && (
        <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-black/60 to-transparent pointer-events-none">
          <p className="text-white text-sm font-medium truncate">{title}</p>
        </div>
      )}
    </div>
  )
}
