# Lost & Found System

A small website where people post things they **lost** or **found**, so the right person can get them back.

**Built with:** React (Vite) for the website, FastAPI + PostgreSQL for the server.

---

## What can you do? (Features)

| Feature | What it means |
|---|---|
| **List** | See all posts, newest first |
| **Search** | Type words (like "wallet" or "library"), filter by Lost / Found and by category |
| **Add (create)** | Fill in a short form to post a lost or found item |
| **Delete** | Remove your own post using your PIN |
| *Bonus:* **Mark as returned** | Close a post when the item is back with its owner |

---

## Pages

| # | Page | Address | What it is for |
|---|---|---|---|
| 1 | **Home** | `/` | Shows all posts. Has the search box, the Lost/Found tabs, and the category filter. Big buttons: "I lost something" and "I found something". |
| 2 | **Report an item** | `/report` | The form to add a new post. |
| 3 | **Post details** | `/items/:id` | Shows one post in full, with contact details. The owner can mark it as returned or delete it here. |
| 4 | **Not found** | any other address | Friendly message with a link back home. |

---

## User flow (in simple English)

### A. I lost something
1. I open the website. The **Home** page shows all posts.
2. I type a word in the search box (for example "keys"). I check if someone already found it.
3. If I see my item, I click it, read the details, and use the contact info to reach the finder.
4. If it is not there, I click **I lost something**.
5. On the **Report an item** page, I fill in: what it is, details, where and when I lost it, my name and contact, and a **PIN**.
6. I click **Post item**. My post is now live, and I see its details page.
7. Later, when I get my item back, I open my post, type my PIN, and click **Mark as returned** (or **Delete post**).

### B. I found something
1. I open the website and click **I found something**.
2. I fill in the form. I keep one small detail secret, so I can check the real owner later.
3. I click **Post item**. The owner can now find it by searching.
4. When someone claims it, I open my post, type my PIN, and click **Mark as returned**.

### C. I am just browsing
1. I open the Home page and use the tabs (All / Lost / Found) and category filter.
2. I click any post to see where and when it happened and who to contact.

### D. I made a mistake or the post is no longer needed
1. I open my post.
2. In the box "Is this your post?", I type my PIN.
3. I click **Delete post**, then **Yes, delete for good**.
4. I am taken back to Home, and the post is gone.

---

## How to run it

`docker compose up`

Open the website at **http://localhost:5173/**. 

---

## API

| Method | Address | What it does |
|---|---|---|
| GET | `/api/items` | List posts. Options: `q` (search words), `status` (`lost`/`found`), `category`, `include_resolved` (`true`/`false`) |
| GET | `/api/items/{id}` | Get one post |
| POST | `/api/items` | Create a post (needs a `pin`) |
| PATCH | `/api/items/{id}/resolve` | Mark as returned. Send the PIN in the `X-Item-PIN` header |
| DELETE | `/api/items/{id}` | Delete a post. Send the PIN in the `X-Item-PIN` header |

A wrong PIN gives a `403` error. A missing post gives `404`. Bad form data gives `422`.

---

## Project structure

```
lost-and-found/
├── backend/
│   ├── app/
│   │   ├── main.py        # API routes (list, search, add, delete, resolve)
│   │   ├── models.py      # database table
│   │   ├── schemas.py     # what data is allowed in and out
│   │   ├── security.py    # PIN hashing
│   │   └── database.py    # SQLite connection
│   ├── seed.py            # sample data (optional)
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── vite.config.js     # sends /api calls to the backend
    └── src/
        ├── main.jsx, App.jsx, api.js, utils.js, styles.css
        ├── components/ItemCard.jsx
        └── pages/ HomePage, ReportPage, ItemPage, NotFoundPage
```

## Good next steps

- Photo upload for each item
- User accounts instead of PINs
- Email alert when a new post matches something you lost
- Pagination when there are many posts
