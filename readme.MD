# Studying Application Scalability

1. Clone the repo content locally in your machine
2. Open a Python virtual environment and activate it
3. Install requirements: `pip install -r requirements.txt`
4. Start the app using the command: `uvicorn app.2_server_ORM:app --reload`

## Scaling a Social Media App: Part 1 – Building the MVP 🚀

Every app starts small—a simple backend that manages users, posts, and interactions. But as traffic grows, the system needs to scale efficiently to handle millions of reads and writes. In this series, I’ll walk through the journey of scaling a social media app, starting from a single backend server and slowly build on top of it, while reasoning

**🏗️ The MVP: FastAPI + PostgreSQL**

For the initial backend, I chose FastAPI for its asynchronous capabilities and rapid development speed, and PostgreSQL for structured data storage. Here's the basic architecture:

**Users Table🧑**: Stores user_id (email for now) and hashed passwords (bcrypt). JWT-based authentication for secure API access.

**Posts Table 📝**: post_id (PK), created_timestamp, visible_flag, owner_id (FK to Users). Basic fields for title, content, etc.

**Likes Table ❤️**: A composite PK (post_id, user_id) ensuring one like per user per post.


**🔹 Why SQL (PostgreSQL) over NoSQL?**

A common question: Why not NoSQL? My reasoning:

 ✅ PostgreSQL is easy to use, scales well for reads & writes, and offers schema enforcement—which helps early-stage development.

 ✅ The initial schema is fixed, making SQL a great starting point.

 ✅ While social media writes scale fast, we can always optimize or switch to NoSQL later if necessary.

**🔹 Why FastAPI?**

FastAPI has gained massive popularity for being:

 ✅ Asynchronous & non-blocking, allowing it to handle more concurrent requests.

 ✅ Lightweight & fast, perfect for API-driven architectures.

 ✅ Automatic validation with Pydantic, reducing boilerplate.

**🛠️ What’s Next? Scaling Challenges Ahead!**

This MVP works great for a small user base, but what happens when millions of users start liking, commenting, and posting? In the next post, I’ll start exploring read optimization within my server, using strategies like:

 ✅ Caching posts using Redis

 ✅ Indexing strategies & query tuning
