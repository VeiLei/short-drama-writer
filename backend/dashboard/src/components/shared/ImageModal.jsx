export default function ImageModal({ src, alt, onClose }) {
  if (!src) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        <img src={src} alt={alt || ''} className="modal-image" />
      </div>
    </div>
  );
}
