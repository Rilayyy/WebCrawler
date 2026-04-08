# CS4700 Web Crawler - README

## High-Level Approach

We implemented a complete HTTP/1.1 client from scratch to crawl Fakebook and foundd 5 secret flags each. Our architecture consists of two main components:

**HttpClient Class**: Handles all HTTP/1.1 protocol implementation including:
- TLS/SSL connection wrapping for HTTPS
- HTTP request formatting with required headers (Host, User-Agent, Connection)
- Response parsing and status code handling
- Cookie extraction and session management
- Chunked transfer encoding decoding

**Crawler Class**: Manages the web crawling logic including:
- Authentication flow with CSRF token extraction
- Frontier management using a queue (deque) for URLs to visit
- Visited URL tracking to prevent infinite loops
- HTML parsing for link and secret flag extraction
- 503 retry logic with exponential backoff

Our crawler follows a systematicc approach: login to Fakebook, then recursively crawl pages while maintaining a frontier of unvisited URLs until all 5 flags are found.

## Challenges Faced

**403 Forbidden Error**: Initially we had encountered 403 errors during login POST requests. The issue was that we missing CSRF tokens and improper cookie handling. We fixed this by:
- Extracting CSRF tokens from login page HTML forms
- Implementing case-insensitive cookie header parsing and
- Adding Referer header for Django CSRF protection

**Session Loss**: Lost authentication session after visiting logout links. We fixed this by explicitly skipping `/accounts/logout/` URLs in the frontier to preserve the session.

**HTTP Response Parsing**: Truncated responses due to incomplete data reading. We fixed this by reading all data until socket closes and implementing proper chunked encoding support.

**503 Service Unavailable**: We implemented retry logic with exponential backoff (1s->2s->4s) as required by the assignment specification.

## Testing Overview

**Authentication Testing**: We verified the login flow works correctly by testing the three-step process:
1. GET login page to extract CSRF token
2. POST credentials with CSRF token
3. GET authenticated page to confirm session

**Crawler Testing**: We tested the crawling logic by:
- Verifying frontier management prevents infinite loops (A->B->A scenario)
- Confirming domain filtering restricts crawling to Fakebook only
- Testing 503 retry behavior with simulated failures
- Validating clean output (only 5 flags to STDOUT)

**Flag Detection Testing**: We confirmed flag extraction works by:
- Testing regex pattern against known flag formats
- Verifying HTML parser correctly identifies secret flags
- Ensuring no duplicate flags are collected

**Final Testing**: We successfully ran the complete crawler and found all 5 secret flags each.