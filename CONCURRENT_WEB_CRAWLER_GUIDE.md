# Concurrent Web Crawler (Java) — Practical Project Guide

This guide helps you build a **production-style, polite concurrent web crawler** in Java.

## 1) Project Goal

Build a crawler that:
- Starts from one or more seed URLs.
- Fetches pages concurrently.
- Parses links from each page.
- Deduplicates URLs so each is visited once.
- Respects `robots.txt` and crawl delays.
- Stores results (title, status code, links found, etc.).

---

## 2) Suggested Tech Stack

- **Java 21+** (works well with modern concurrency APIs).
- **HttpClient** (`java.net.http`) for HTTP requests.
- **jsoup** for HTML parsing and link extraction.
- **Maven** (or Gradle) as build tool.

---

## 3) Core Architecture

Use a producer-consumer design:

1. **Frontier Queue**: URLs waiting to be crawled.
2. **Visited Set**: Thread-safe set of already-seen URLs.
3. **Worker Pool**: Multiple workers fetch and parse pages.
4. **Result Sink**: Persist crawl output (console/JSON/DB).
5. **Politeness Manager**: Per-host rate limiting + robots checks.

### Thread-safe data structures

- `BlockingQueue<URI>` for the frontier.
- `ConcurrentHashMap.newKeySet()` for visited URLs.
- `ConcurrentHashMap<String, Instant>` for host throttling metadata.

---

## 4) Minimal Crawl Flow

Each worker repeats:

1. Take URL from queue.
2. Canonicalize URL (normalize scheme/host/path).
3. Skip if already visited.
4. Check robots permission.
5. Wait if host rate limit requires delay.
6. Fetch page (timeout + redirect policy).
7. If HTML, parse links using jsoup.
8. Filter/normalize child links and enqueue new URLs.
9. Store result + metrics.

---

## 5) Starter Code Skeleton

```java
public final class CrawlerEngine {
    private final BlockingQueue<URI> frontier = new LinkedBlockingQueue<>();
    private final Set<URI> visited = ConcurrentHashMap.newKeySet();
    private final ExecutorService pool;
    private final HttpClient client;

    public CrawlerEngine(int workers) {
        this.pool = Executors.newFixedThreadPool(workers);
        this.client = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public void start(List<URI> seeds, int maxPages) throws InterruptedException {
        seeds.forEach(frontier::offer);
        AtomicInteger crawled = new AtomicInteger(0);

        for (int i = 0; i < ((ThreadPoolExecutor) pool).getCorePoolSize(); i++) {
            pool.submit(() -> workerLoop(maxPages, crawled));
        }

        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.MINUTES);
    }

    private void workerLoop(int maxPages, AtomicInteger crawled) {
        while (!Thread.currentThread().isInterrupted()) {
            if (crawled.get() >= maxPages) return;
            URI url;
            try {
                url = frontier.poll(2, TimeUnit.SECONDS);
                if (url == null) return;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }

            URI norm = UrlNormalizer.normalize(url);
            if (!visited.add(norm)) continue;

            CrawlResult result = fetchAndParse(norm);
            if (result.links() != null) {
                for (URI link : result.links()) {
                    frontier.offer(link);
                }
            }
            crawled.incrementAndGet();
            ResultStore.write(result);
        }
    }

    private CrawlResult fetchAndParse(URI uri) {
        // robots + politeness checks here
        // HTTP fetch with client.send(...)
        // parse HTML with Jsoup.parse(body, uri.toString())
        return CrawlResult.error(uri, "Not implemented");
    }
}
```

---

## 6) URL Normalization Rules (Important)

Use consistent rules before adding to `visited`:

- Lowercase scheme + host.
- Remove default ports (`:80` for HTTP, `:443` for HTTPS).
- Remove fragments (`#section`).
- Resolve relative URLs against base URL.
- Optionally sort query parameters.
- Ignore non-http(s) schemes (`mailto:`, `javascript:`).

This dramatically reduces duplicate crawling.

---

## 7) robots.txt and Politeness

Implement host-level crawl politeness:

- Fetch `/robots.txt` once per host and cache rules.
- Respect `Disallow` for your user-agent (`*` fallback).
- Respect `Crawl-delay` if present.
- Add a minimum fixed delay per host (e.g., 300–1000ms) even if not specified.

> In interviews and real projects, this is often the difference between a toy crawler and a professional one.

---

## 8) Concurrency Strategy (Simple & Good)

Start with:
- `Executors.newFixedThreadPool(workers)`
- Worker count around `2 * availableProcessors()` for I/O-heavy crawling.

Then tune by measuring:
- Queue size growth.
- Avg response time per host.
- Throughput (pages/sec).
- Error rates (timeouts, 429, 5xx).

---

## 9) Failure Handling & Retries

- Set connect + read timeouts.
- Retry transient errors (`429`, `503`, timeouts) with exponential backoff.
- Cap retries (e.g., max 2 or 3).
- Keep a dead-letter log for permanently failed URLs.

---

## 10) Data Model Suggestion

```java
public record CrawlResult(
    URI url,
    int statusCode,
    String contentType,
    String title,
    List<URI> links,
    String error,
    Instant fetchedAt,
    long latencyMs
) {
    static CrawlResult error(URI url, String error) {
        return new CrawlResult(url, -1, null, null, List.of(), error, Instant.now(), -1);
    }
}
```

---

## 11) Suggested Project Structure

```text
src/main/java/com/example/crawler/
  CrawlerApp.java
  CrawlerEngine.java
  Fetcher.java
  HtmlParser.java
  UrlNormalizer.java
  RobotsManager.java
  HostRateLimiter.java
  ResultStore.java
  model/CrawlResult.java
```

---

## 12) MVP Milestones (Do in Order)

1. Single-thread crawl with visited set.
2. Add fixed thread pool.
3. Add robust URL normalization.
4. Add robots.txt support.
5. Add host rate limiting.
6. Add retries + metrics.
7. Persist results to JSON/SQLite.

---

## 13) Example Maven Dependencies

```xml
<dependencies>
  <dependency>
    <groupId>org.jsoup</groupId>
    <artifactId>jsoup</artifactId>
    <version>1.21.2</version>
  </dependency>
</dependencies>
```

(HTTP client comes from JDK, no extra dependency required.)

---

## 14) Demo Scope for College/Interview

For a clean submission:
- Limit crawl to one domain.
- Max pages: 500–2000.
- Output top 20 most-linked pages.
- Show metrics dashboard in console:
  - total crawled
  - success/fail counts
  - avg latency
  - queue size

---

## 15) Common Pitfalls

- Using non-thread-safe collections.
- Not canonicalizing URLs.
- No stop condition (crawler runs forever).
- Ignoring robots/politeness.
- Flooding one host with many concurrent requests.

---

## 16) What to Tell Your Professor

- You implemented a **concurrent producer-consumer crawler**.
- You ensured **thread safety** with concurrent collections.
- You improved quality with **URL canonicalization + robots compliance**.
- You made it scalable with a **worker pool + host throttling + retries**.

---

## 17) Next Step (If you want, I can generate it)

Ask for: **"Give me full runnable Java Maven code for this crawler"** and you can get:
- Complete class-by-class implementation.
- `pom.xml`.
- Sample run command.
- Test strategy.
