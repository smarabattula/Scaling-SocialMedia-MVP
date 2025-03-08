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

## Part 2 – Optimizing Reads for Performance
As we scale beyond an MVP, one of the first bottlenecks is read-heavy traffic. A social media app involves frequent feed queries, profile lookups, and trending posts, making efficient reads critical to performance. Here’s how we optimize reads as traffic grows.
🔹 The Problem: Scaling Reads Efficiently
As posts and users grow, fetching feeds becomes expensive. Querying millions of rows for searching posts can overwhelm PostgreSQL DB, leading to slow response times. Instead of immediately scaling PostgreSQL horizontally, we apply optimizations to reduce DB load.

📌 Strategy 1: **Indexing for Faster Queries**

✅ Composite Index (created_timestamp, owner_id) – Speeds up filtering posts by user. Can also be used to pull feed. 

✅ Partial Indexes – Index only active posts (WHERE visible_flag = TRUE). 

✅ BRIN Index for Large Datasets – Works well for sequential timestamps.

I'm currently implementing composite index, and studied in-depth about types of database indexes, and clustered vs non-clustered index, which come very handy in usecases. For this app, clustered indices are best for feed, while non-clustered(secondary) indices are best for lookup(search). 

📌 Strategy 2: **Read Replicas for Scaling Reads**

✅ Primary DB (Writes Only) – Handles inserts for posts, likes, comments. 

✅ Read Replicas (Read Queries Only) – Feeds, user lookups, post queries.

✅ Load Balancing – (Can be little complex, let's discuss and work on it later)

📌 Strategy 3: **Caching for High-Speed Reads**

✅ Redis Cache – Store latest results instead of querying the DB 

✅ User Profiles, Post Metadata and Likes Counter in Redis – Reduce workload on DB by asynchronous communication with DB, while maintaining consistency in likes 

✅ Cache Expiry & Invalidation – Initially I set TTL for event-driven updates in Redis (Records expire after certain time, I'm still exploring other options). 

📌 Strategy 4: **Precomputed Feeds for Instant Retrieval**

✅ Denormalized Feed Table – Store precomputed post metadata in cache (Ex: Likes) 

✅ Event-Driven Updates – Use async/await capabilities of FastAPI & Python.

🚀 What's Next? Scaling Writes & Async Processing
Now that reads are optimized, next we handle massive writes from likes, comments, and posts. In Part 3, we’ll explore:

✅ Partitioning & Batching for High-Write Scaling 

✅ Async Processing to Reduce DB Load 

✅ Event-Driven Architecture for Write Optimization 

✅ Redis caching policies (invalidation, eviction) 

✅ Database Replica Load Balancing
