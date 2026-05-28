import { getVideoUrl } from '../lib/api'
export default function VideoPlayer({ taskId }) {
  return (
    <div className="w-full rounded-xl overflow-hidden bg-black border border-forge-border">
      <video controls className="w-full max-h-[480px] object-contain" src={getVideoUrl(taskId)}>Seu navegador não suporta vídeo.</video>
    </div>
  )
}
