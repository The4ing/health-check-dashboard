from flask import Flask, jsonify, render_template, request, redirect, url_for, Response
import requests
import time
import os
import re
import ipaddress
from urllib.parse import urlparse
from pathlib import Path
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


# ---- Prometheus metrics ----
SITE_CHECKS = Counter("site_checks_total", "Total site checks", ["site", "status"])
RESPONSE_TIME = Histogram(
    "site_response_time_seconds",
    "Response time per site (seconds)",
    ["site"],
)


app = Flask(__name__)

# savingfiles path
# Windows: $env:DATA_DIR="$PWD\data")
DATA_DIR = os.getenv("DATA_DIR", "/data")
SITES_FILE = Path(DATA_DIR) / "sites.txt"

DEFAULT_SITES = [
    "https://google.com",
    "https://cyberark.com",
    "https://github.com",
]

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (HealthCheckBot/1.0)"}

# Regex for correct domain
HOSTNAME_RE = re.compile(r"^(localhost|([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63})$")

def is_valid_url(u: str) -> bool:
    try:
        if not isinstance(u, str):
            return False
        u = u.strip()
        if not u or any(ch.isspace() for ch in u):
            return False

        if "://" not in u:
            u = "https://" + u

        p = urlparse(u)
        if p.scheme not in ("http", "https"):
            return False

        host = p.hostname
        if not host:
            return False

        # legel IP b
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            pass

        # valid domain or localhost
        return HOSTNAME_RE.fullmatch(host) is not None
    except Exception:
        return False


def normalize_url(u: str) -> str:
    u = u.strip()
    if not u:
        return u
    if "://" not in u:
        u = "https://" + u
    if len(u) > 1 and u.endswith("/"):
        u = u[:-1]
    return u


def dedup(items):
    seen, out = set(), []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def load_sites():
    # 1) sites.txt (Persisted)
    if SITES_FILE.exists():
        with open(SITES_FILE, "r", encoding="utf-8") as f:
            sites = [normalize_url(ln) for ln in f if ln.strip()]
        sites = [s for s in sites if is_valid_url(s)]
        if sites:
            return dedup(sites)

    # 2) SITES env (Ephemeral)
    env_val = os.getenv("SITES")
    if env_val:
        sites = [normalize_url(s) for s in env_val.split(",") if s.strip()]
        sites = [s for s in sites if is_valid_url(s)]
        if sites:
            return dedup(sites)

    # 3) default (First run)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SITES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(DEFAULT_SITES) + "\n")
    return DEFAULT_SITES[:]

SITES = load_sites()

def save_sites():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SITES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(SITES) + "\n")

def check_sites():
    results = []
    for site in SITES:
        start = time.time()
        status = "DOWN"
        try:
            r = requests.get(site, headers=HTTP_HEADERS, timeout=5)
            if 200 <= r.status_code < 400:
                status = "UP"
        except Exception:
            status = "DOWN"

        dt = time.time() - start
        RESPONSE_TIME.labels(site=site).observe(dt)
        SITE_CHECKS.labels(site=site, status=status).inc()

        results.append(
            {"site": site, "status": status, "response_time_ms": round(dt * 1000, 2)}
        )
    return results


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api")
def api():
    data = check_sites()
    up = sum(1 for x in data if x["status"] == "UP")
    return jsonify({"summary": {"up": up, "total": len(data)}, "results": data})


@app.route("/", methods=["GET"])
def home():
    data = check_sites()
    up = sum(1 for x in data if x["status"] == "UP")
    return render_template(
        "index.html", results=data, summary={"up": up, "total": len(data)}, sites=SITES
    )

@app.route("/add-site", methods=["POST"])
def add_site():
    new_site = normalize_url((request.form.get("site") or ""))
    if new_site and is_valid_url(new_site) and new_site not in SITES:
        SITES.append(new_site)
        SITES[:] = dedup(SITES)
        save_sites()
    return redirect(url_for("home"))

@app.route("/remove-site", methods=["POST"])
def remove_site():
    target = normalize_url((request.form.get("site") or ""))
    if target in SITES:
        SITES.remove(target)
        save_sites()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
