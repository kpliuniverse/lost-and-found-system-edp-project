import { Link } from "react-router-dom";
import { formatDate, statusLabel } from "../utils.js";
import { getImageUrl } from "../api.js";

export default function ItemCard({ item }) {
  return (
    <Link to={`/items/${item.id}`} className={`tag tag--${item.status}`}>
      <div className="tag__top">
        <span className={`chip chip--${item.status}`}>{statusLabel(item.status)}</span>
        {item.is_resolved && <span className="chip chip--returned">Returned</span>}
      </div>
      <h3 className="tag__title">{item.title}</h3>
      <img style={{width: "100%"}} src={getImageUrl(item.image_filenames[0].filename)}/>
      <p className="tag__meta">{item.category}</p>
      <p className="tag__meta">{item.location}</p>
      <p className="tag__meta">{formatDate(item.event_date)}</p>
    </Link>
  );
}
