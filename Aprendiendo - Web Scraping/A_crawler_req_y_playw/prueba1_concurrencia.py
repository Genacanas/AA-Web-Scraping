import asyncio, httpx
from urllib.parse import urljoin, urlparse

CONTACT_PATTERNS = ["/contacto", "/contacto.html", "/contacto.php"]
SKIP_STATUS = {400, 404, 410, 422}
MAX_CONCURRENCY = 20
PER_DOMAIN_LIMIT = 3


def domain_of(url: str) -> str:
    return urlparse(url).netloc


class RateLimiter:
    def __init__(self, per_domain=PER_DOMAIN_LIMIT, global_limit=MAX_CONCURRENCY):
        self.global_sem = asyncio.Semaphore(global_limit)
        self._by_host = {}
        self.per_domain = per_domain

    def sem(self, url: str) -> asyncio.Semaphore:
        host = domain_of(url)
        if host not in self._by_host:
            self._by_host[host] = asyncio.Semaphore(self.per_domain)
        return self._by_host[host]


limiter = RateLimiter()


async def fetch(client: httpx.AsyncClient, url: str):
    backoffs = [0.2, 0.6, 1.2]
    async with limiter.global_sem, limiter.sem(url):
        for i, wait in enumerate(backoffs):
            try:
                r = await client.get(url, timeout=15)
                if r.status_code in (429, 500, 502, 503, 504) and i < len(backoffs) - 1:
                    await asyncio.sleep(wait)
                    continue
                return r.status_code, r.text
            except httpx.RequestError:
                if i == len(backoffs) - 1:
                    return None, None
                await asyncio.sleep(wait)
    return None, None


def extract_emails(html: str) -> set[str]:
    # tu extractor real aquí
    return set()


async def process_seed(client: httpx.AsyncClient, seed: dict) -> dict:
    root = seed["url"]

    # Home
    st, txt = await fetch(client, root)
    if st is None or st in SKIP_STATUS:
        return {"seed": seed, "result": None, "reason": f"skip_{st}_home"}
    if st != 200:
        return {"seed": seed, "result": None, "reason": f"status_{st}_home"}

    emails = extract_emails(txt)
    if emails:
        return {
            "seed": seed,
            "result": {
                "source": "home_HTML",
                "source_url": root,
                "emails": list(emails),
            },
        }

    # Contactos (secuencial por seed)
    for suf in CONTACT_PATTERNS:
        url = urljoin(root, suf)
        st, txt = await fetch(client, url)
        if st is None or st in SKIP_STATUS:
            continue
        if st != 200:
            continue
        emails = extract_emails(txt)
        if emails:
            return {
                "seed": seed,
                "result": {
                    "source": "contact_HTML",
                    "source_url": url,
                    "emails": list(emails),
                },
            }
        # 200 sin emails → cortar
        return {"seed": seed, "result": None, "reason": "contact_200_no_emails_stop"}

    return {"seed": seed, "result": None, "reason": "no_emails_html_phase"}


async def run_html_phase(seeds: list[dict]) -> tuple[list[dict], list[dict]]:
    results, pending_js = [], []
    async with httpx.AsyncClient(
        http2=True,
        headers={
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 ...",
        },
    ) as client:
        tasks = [process_seed(client, s) for s in seeds]
        for coro in asyncio.as_completed(tasks):
            r = await coro
            seed = r["seed"]
            if r.get("result"):
                out = {
                    "seed_id": seed.get("id"),
                    "seed_title": seed.get("title"),
                    "site_root": seed["url"],
                    **r["result"],
                }
                results.append(out)
            else:
                if r["reason"] in {
                    "no_emails_html_phase",
                    "status_401_home",
                    "status_403_home",
                    "status_429_home",
                }:
                    pending_js.append(seed)
    return results, pending_js


# Uso:
# html_results, pending = asyncio.run(run_html_phase(seeds))
# Luego corrés Playwright sobre 'pending'
