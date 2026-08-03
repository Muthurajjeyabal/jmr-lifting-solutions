# Cloudflare Cache Rules — jmrlifting.com

Since GitHub Pages doesn't set aggressive cache headers, configure these Cache Rules in the Cloudflare dashboard for `jmrlifting.com`.

## Path: Rules → Cache Rules → Create rule

### Rule 1 — Long-cache static assets (fonts, images, JS, CSS)

**When incoming requests match:**
- URI Path → `matches regex` → `\.(css|js|webp|jpg|jpeg|png|gif|svg|woff2|woff|ttf|ico)$`

**Then:**
- Cache eligibility → **Eligible for cache**
- Edge TTL → **Override → 1 year** (31536000 s)
- Browser TTL → **Override → 1 year** (31536000 s)
- Serve stale content while updating → **On**

### Rule 2 — Short-cache HTML (so content updates go live fast)

**When incoming requests match:**
- URI Path → `ends with` → `.html`  **OR**  URI Path → `equals` → `/`

**Then:**
- Cache eligibility → **Eligible for cache**
- Edge TTL → **Override → 5 minutes** (300 s)
- Browser TTL → **Override → 5 minutes** (300 s)

### Rule 3 — Never cache service worker

**When incoming requests match:**
- URI Path → `equals` → `/sw.js`  **OR**  URI Path → `equals` → `/manifest.json`

**Then:**
- Cache eligibility → **Bypass cache**

### Rule 4 — Never cache Formspree/Uploadcare/GA (already handled — external hosts, but confirm no proxying)

## Additional recommendations

- **Speed → Optimization → Brotli** → On
- **Speed → Optimization → Auto Minify** → Off (files are already minified in build; Cloudflare's minifier occasionally breaks inline JS)
- **Speed → Optimization → Early Hints** → On (sends preload hints before HTML ready)
- **Caching → Configuration → Browser Cache TTL** → Respect Existing Headers
- **Speed → Optimization → HTTP/3 (with QUIC)** → On

## Verify with

```bash
curl -sI https://jmrlifting.com/assets/images/jmr_hero-640w.webp | grep -i "cache-control\|cf-cache-status"
```

Should show `cache-control: public, max-age=31536000` and `cf-cache-status: HIT` after warm-up.
