import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { createItem, getImageUrl, uploadImage } from "../api.js";
import { CATEGORIES, todayISO } from "../utils.js";

const MAX_IMAGES = 8;
const MAX_IMAGE_SIZE = 8 * 1024 * 1024;

export default function ReportPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [form, setForm] = useState({
    status: params.get("type") === "found" ? "found" : "lost",
    title: "",
    category: CATEGORIES[0],
    description: "",
    location: "",
    event_date: todayISO(),
    contact_name: "",
    contact_info: "",
    pin: "",
  });
  const [images, setImages] = useState([]);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");
  const isLost = form.status === "lost";

  function update(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function selectImages(e) {
    const selected = Array.from(e.target.files ?? []);
    e.target.value = "";

    if (images.length + selected.length > MAX_IMAGES) {
      setError(`You can only upload up to ${MAX_IMAGES} images.`);
      return;
    }
    if (selected.some((file) => !file.type.startsWith("image/"))) {
      setError("Please select image files only.");
      return;
    }

    if (selected.some((file) => file.size > MAX_IMAGE_SIZE)) {
      setError("Each image must be 8MB or smaller.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError("");
    try {
      const totalBytes = selected.reduce((total, file) => total + file.size, 0);
      let completedBytes = 0;
      for (const file of selected) {
        const { location } = await uploadImage(file, (loaded) => {
          const currentBytes = completedBytes + Math.min(loaded, file.size);
          setUploadProgress(totalBytes ? Math.round((currentBytes / totalBytes) * 100) : 100);
        });
        const filename = location?.split("/").pop();
        if (!filename) {
          throw new Error(`The upload response for "${file.name}" did not include a filename.`);
        }
        setImages((current) => [...current, { file, filename }]);
        completedBytes += file.size;
        setUploadProgress(totalBytes ? Math.round((completedBytes / totalBytes) * 100) : 100);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function submit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const item = await createItem({
        ...form,
        image_filenames: images.map(({ filename }) => filename),
      });
      navigate(`/items/${item.id}`, {
        state: { notice: "Your post is live. Keep your PIN safe: you need it to delete or close the post." },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="narrow">
      <Link to="/" className="back">
        Back to all posts
      </Link>
      <h1>Report an item</h1>

      <form onSubmit={submit} className="form">
        <fieldset className="switch">
          <legend>What happened?</legend>
          <label className={isLost ? "is-active is-lost" : ""}>
            <input type="radio" name="status" value="lost" checked={isLost} onChange={update} />I lost something
          </label>
          <label className={!isLost ? "is-active is-found" : ""}>
            <input type="radio" name="status" value="found" checked={!isLost} onChange={update} />I found something
          </label>
        </fieldset>

        <label className="field">
          What is it?
          <input
            name="title"
            value={form.title}
            onChange={update}
            placeholder="Example: Black leather wallet"
            minLength={3}
            maxLength={120}
            required
          />
        </label>

        <label className="field">
          Category
          <select name="category" value={form.category} onChange={update}>
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>

        <label className="field">
          Details (color, brand, marks)
          <textarea
            name="description"
            value={form.description}
            onChange={update}
            rows={4}
            maxLength={2000}
            placeholder={
              isLost
                ? "Anything that helps someone recognize it."
                : "Describe it, but keep one detail secret so you can check the real owner."
            }
          />
        </label>

        <div className="row">
          <label className="field">
            Where was it {isLost ? "lost" : "found"}?
            <input name="location" value={form.location} onChange={update} minLength={2} maxLength={160} required />
          </label>
          <label className="field">
            Date
            <input type="date" name="event_date" value={form.event_date} max={todayISO()} onChange={update} required />
          </label>
        </div>

        <div className="row">
          <label className="field">
            Your name
            <input name="contact_name" value={form.contact_name} onChange={update} minLength={2} maxLength={80} required />
          </label>
          <label className="field">
            Email or phone
            <input name="contact_info" value={form.contact_info} onChange={update} minLength={3} maxLength={120} required />
          </label>
        </div>

        <div className="row">
          <label className="field entirerow">
            Images
            <input
              type="file"
              name="images"
              accept="image/*"
              multiple
              disabled={saving || uploading}
              onChange={selectImages}
            />
            <small>
              Optional. Select up to {MAX_IMAGES} images. 8MB limit. Click on image to remove from post.
              {uploading && " Uploading images…"}
            </small>
            {uploading && (
              <div className="upload-progress">
                <progress value={uploadProgress} max="100" aria-label="Image upload progress" />
                <span>{uploadProgress}%</span>
              </div>
            )}

          </label>
          {images.length > 0 && (
              // <ul>
              //   {images.map(({ file, filename }, index) => (
              //     <li key={`${filename}-${index}`}>
              //       {filename}{" "}
              //       <button
              //         type="button"
              //         disabled={saving || uploading}
              //         onClick={() => setImages((current) => current.filter((_, i) => i !== index))}
              //         aria-label={`Remove ${file.name}`}
              //       >
              //         Remove
              //       </button>
              //     </li>
              //   ))}
              // </ul>
            <div className="uploadedImagePreview">
                {images.map(({filename}, index) => <img src={getImageUrl(filename)} onClick={() => setImages((current) => current.filter((_, i) => i !== index))}/>)}
            </div>
        )}
        </div>
        <label className="field">
          Choose a PIN (4 to 20 characters)
          <input
            name="pin"
            type="password"
            value={form.pin}
            onChange={update}
            minLength={4}
            maxLength={20}
            autoComplete="new-password"
            required
          />
          <small>You will need this PIN to delete or close your post. We cannot recover it.</small>
        </label>

        {error && (
          <p className="banner banner--error" role="alert">
            {error}
          </p>
        )}

        <button className="btn" disabled={saving || uploading}>
          {uploading ? "Uploading…" : saving ? "Posting…" : "Post item"}
        </button>
      </form>
    </section>
  );
}
