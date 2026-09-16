#!/usr/bin/env bash
# htb-web-recon.sh — HTB web enumeration orchestrated around established tools.
#
# Scanning engines are NOT reimplemented here:
#   feroxbuster / ffuf / gobuster  -> content discovery + vhost fuzzing
#   whatweb                        -> fingerprinting
#   nikto (-k)                     -> well-known misconfig/vuln checks (opt-in)
#   nmap                           -> service/version scan (opt-in)
#   openssl                        -> TLS certificate SANs
#   curl                           -> glue probes (UA diff, 403 bypass, CORS,
#                                     robots/sitemap, comments, JS secrets)
#
# Usage:
#   ./htb-web-recon.sh http://10.10.10.5 [options]
#   ./htb-web-recon.sh 10.10.10.5 -p 8080 --domain staff.htb --nikto
set -uo pipefail

VERSION="1.0"

# ---------------------------------------------------------------- output ---
if [ -t 1 ]; then
    C_R=$'\033[0m'; C_B=$'\033[1m'; C_DIM=$'\033[2m'
    C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YEL=$'\033[33m'
    C_CY=$'\033[36m'; C_MAG=$'\033[35m'
else
    C_R=""; C_B=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YEL=""; C_CY=""; C_MAG=""
fi

OUT=""
banner() { printf '%s\n%s\n%s\n' "${C_B}${C_CY}$1${C_R}" \
    "${C_DIM}────────────────────────────────────────────────────────────────${C_R}" ""; }
info()  { printf '  %s[i]%s %s\n' "$C_CY" "$C_R" "$1"; }
good()  { printf '  %s[+]%s %s\n' "$C_GREEN" "$C_R" "$1"; }
warn()  { printf '  %s[!]%s %s\n' "$C_YEL" "$C_R" "$1"; }
die()   { printf '  %s[x]%s %s\n' "$C_RED" "$C_R" "$1" >&2; exit 1; }

# ------------------------------------------------------------- wordlists ---
pick_wordlist() {
    local cands=(
        "$WORDLIST"
        /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
        /usr/share/seclists/Discovery/Web-Content/common.txt
        /usr/share/wordlists/dirb/common.txt
        /usr/share/wordlists/wfuzz/wordlist/general/common.txt
    )
    for f in "${cands[@]}"; do
        [ -n "$f" ] && [ -f "$f" ] && { echo "$f"; return; }
    done
    echo ""
}

pick_vhost_list() {
    local cands=(
        /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
        /usr/share/wordlists/dnsmap.txt
    )
    for f in "${cands[@]}"; do
        [ -f "$f" ] && { echo "$f"; return; }
    done
    echo ""
}

# ------------------------------------------------------------------ CLI ---
TARGET=""
PORT=""
DOMAIN=""
WORDLIST=""
THREADS=50
DEPTH=3
EXTENSIONS="php,html,bak,old,txt,zip,sql,json,orig,save"
COOKIES=""
PROXY=""
RUN_NIKTO=0 RUN_NMAP=0 ACTIVE_METHODS=0 RUN_NUCLEI=0 DEFAULT_CREDS=0
AUTH_USER=""; AUTH_PASS=""; AUTH_LOGIN=""; DIFF_DIR=""
DO_VHOST=1 DO_UA=1 DO_BYPASS=1 DO_JS=1 DO_CONTENT=1
EXTRA_HDRS=()

usage() {
    cat <<'SYN'

USAGE (target is required — IP or URL, first argument):
  ./htb-web-recon.sh <target> [flags]

EXAMPLES:
  ./htb-web-recon.sh 10.10.10.5                     # default scan, all phases
  ./htb-web-recon.sh http://10.10.10.5:8080         # explicit scheme/port
  ./htb-web-recon.sh 10.10.10.5 -d connected.htb    # + known domain (vhost fuzzing)
  ./htb-web-recon.sh 10.10.10.5 -H "Host: x.htb"    # scan one specific vhost
  ./htb-web-recon.sh 10.10.10.5 --nikto --nmap      # + optional deep scans

SYN
    cat <<'FLAGS'

  Scanning engines are NOT reimplemented here:
    feroxbuster / ffuf / gobuster  -> content discovery + vhost fuzzing
    whatweb                        -> fingerprinting
    nikto                          -> well-known misconfig/vuln checks (opt-in)
    nmap                           -> full-port service/version scan (opt-in)
    openssl                        -> TLS certificate SANs
    curl                           -> glue probes (UA diff, 403 bypass, CORS,
                                      robots/sitemap, comments, JS secrets)

flags:
  -p PORT            port (default 80/443 auto)
  -d, --domain DOM   domain for vhost fuzzing (e.g. staff.htb)
  -w, --wordlist F   content wordlist (default: auto-detect seclists/dirb)
  -t, --threads N    concurrency (default 50)
  --depth N          recursion depth for content discovery (default 3)
  -x, --extensions   comma-separated extension list
  -H "K: V"          extra header (repeatable)
  --cookies STR      Cookie header value
  --proxy URL        HTTP proxy for all tools (Burp: http://127.0.0.1:8080)
  --nikto            also run nikto
  --nmap             also run nmap service/version scan
  --active-methods   actively verify PUT writability (writes+deletes a marker
                     file; the default method audit is read-only)
  -U/--auth-user U   credentials for automatic login (POSTs to --auth-login
  -P/--auth-pass P   URL or the first discovered login form), then re-scans
                     with the session and reports paths only visible logged-in
  --auth-login URL   login endpoint to POST credentials to (default: auto)
  --diff OLDDIR      compare against a previous scan; report new paths
  --nuclei           opt-in: run nuclei templates against the target
  --no-vhost|--no-ua|--no-bypass|--no-js|--no-content   skip a phase
  -o DIR             output directory (default webscan_<host>_<ts>)
  -h                 this help
FLAGS
    exit 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        -p|--port) PORT="${2:?}"; shift 2 ;;
        -d|--domain) DOMAIN="${2:?}"; shift 2 ;;
        -w|--wordlist) WORDLIST="${2:?}"; shift 2 ;;
        -t|--threads) THREADS="${2:?}"; shift 2 ;;
        --depth) DEPTH="${2:?}"; shift 2 ;;
        -x|--extensions) EXTENSIONS="${2:?}"; shift 2 ;;
        -H|--header) EXTRA_HDRS+=("${2:?}"); shift 2 ;;
        --cookies) COOKIES="${2:?}"; shift 2 ;;
        --proxy) PROXY="${2:?}"; shift 2 ;;
        --nikto) RUN_NIKTO=1; shift ;;
        --nmap) RUN_NMAP=1; shift ;;
        --no-vhost) DO_VHOST=0; shift ;;
        --active-methods) ACTIVE_METHODS=1; shift ;;
        --nuclei) RUN_NUCLEI=1; shift ;;
        --default-creds) DEFAULT_CREDS=1; shift ;;
        --diff) DIFF_DIR="${2:?}"; shift 2 ;;
        -U|--auth-user) AUTH_USER="${2:?}"; shift 2 ;;
        -P|--auth-pass) AUTH_PASS="${2:?}"; shift 2 ;;
        --auth-login) AUTH_LOGIN="${2:?}"; shift 2 ;;
        --no-ua) DO_UA=0; shift ;;
        --no-bypass) DO_BYPASS=0; shift ;;
        --no-js) DO_JS=0; shift ;;
        --no-content) DO_CONTENT=0; shift ;;
        -o|--output) OUT="${2:?}"; shift 2 ;;
        -h|--help) usage ;;
        -*) die "unknown flag: $1 (see -h)" ;;
        *) [ -n "$TARGET" ] && die "one target only"; TARGET="$1"; shift ;;
    esac
done
if [ -z "$TARGET" ]; then
    printf '%s[x]%s no target given — the IP/URL is a required argument\n' \
        "$C_RED" "$C_R" >&2
    usage
fi
command -v curl >/dev/null || die "curl is required"

printf '%s\n' "${C_B}${C_CY}HTB WEB RECON (established-tools orchestrator) v$VERSION${C_R}"
printf '%s\n' "${C_DIM}authorized targets only — HTB labs / pentest ranges${C_R}"

# ------------------------------------------------- target normalization ---
SCHEME=""
HOST=""
BASEPATH="/"
if [[ "$TARGET" =~ ^https?:// ]]; then
    SCHEME="${TARGET%%://*}"
    REST="${TARGET#*://}"
else
    REST="$TARGET"
fi
HOSTPORT="${REST%%/*}"
[ "$HOSTPORT" != "$REST" ] && BASEPATH="/${REST#*/}"
HOST="${HOSTPORT%%:*}"
[ "$HOST" = "$HOSTPORT" ] || PORT="${HOSTPORT##*:}"
[ -n "$PORT" ] || { [ "$SCHEME" = https ] && PORT=443 || PORT=80; }
[ -n "$SCHEME" ] || SCHEME=http

# ---------------------------------------------------------------- preflight ---
banner "[0] PREFLIGHT"
have() { command -v "$1" >/dev/null 2>&1; }
for t in feroxbuster ffuf gobuster; do
    if have "$t"; then ENGINE="$t"; break; fi
done
[ -n "${ENGINE:-}" ] || die "need feroxbuster, ffuf, or gobuster (apt install feroxbuster)"
have whatweb || warn "whatweb missing — fingerprinting will be curl-only"
WL="$(pick_wordlist)"
[ -n "$WL" ] || die "no wordlist found — install seclists or pass -w"
VHOSTLIST="$(pick_vhost_list)"
info "engine: $ENGINE | wordlist: $WL"
[ -n "$VHOSTLIST" ] && info "vhost list: $VHOSTLIST" \
    || info "vhost list: built-in names"

[ -n "$OUT" ] || OUT="webscan_${HOST}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/console.log") 2>&1

# shared curl arguments (array so quoting stays sane)
CURL_ARGS=(-s -m 15 -k)
[ -n "$PROXY" ] && CURL_ARGS+=(-x "$PROXY")
for h in "${EXTRA_HDRS[@]:-}"; do [ -n "$h" ] && CURL_ARGS+=(-H "$h"); done
[ -n "$COOKIES" ] && CURL_ARGS+=(-b "$COOKIES")
TOOL_HDRS=()
[ -n "$COOKIES" ] && TOOL_HDRS+=("Cookie: $COOKIES")
for h in "${EXTRA_HDRS[@]:-}"; do [ -n "$h" ] && TOOL_HDRS+=("$h"); done

# connectivity probe
code="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' \
    "${SCHEME}://${HOST}:${PORT}${BASEPATH}")" \
    || die "cannot connect to ${SCHEME}://${HOST}:${PORT}"
[ "$code" = "000" ] && die "cannot connect to ${SCHEME}://${HOST}:${PORT}"

BASE="${SCHEME}://${HOST}:${PORT}${BASEPATH}"
info "target: $BASE (root gave HTTP $code)"

# ------------------------- canonical redirect follow (scheme/vhost upgrade) ---
# HTB pattern: http://IP -> https://box.htb/ or http://IP -> http://box.htb/.
# Follow up to 3 hops, switching scheme/port and adopting the vhost Host
# header when the server proves it routes by name (by-IP still redirects).
VH=""
for _hop in 1 2 3; do
    case "$code" in 301|302|307|308) ;; *) break ;; esac
    loc="$(curl "${CURL_ARGS[@]}" -D - -o /dev/null "$BASE" | tr -d '\r' \
        | awk 'tolower($1)=="location:"{print $2; exit}')"
    [ -z "$loc" ] && break
    lscheme="$(printf '%s' "$loc" | sed -nE 's#^(https?)://.*#\1#p')"
    [ -z "$lscheme" ] && break
    _rest="${loc#*://}"
    _hp="${_rest%%[/?#]*}"
    lhost="${_hp%%:*}"
    lport="${_hp#*:}"
    if [ "$lport" = "$_hp" ]; then
        # no explicit port in the Location: same-scheme redirects stay on
        # the listener we are already talking to; scheme upgrades take the
        # scheme's standard port
        if [ "$lscheme" = "$SCHEME" ]; then
            lport="$PORT"
        else
            [ "$lscheme" = https ] && lport=443 || lport=80
        fi
    fi
    # stop when the redirect points at where we already are
    if [ "$lhost" = "$HOST" ] && [ "$lscheme" = "$SCHEME" ] \
        && [ "$lport" = "$PORT" ]; then break; fi
    # never chase redirects to a different numeric IP
    if [[ "$lhost" =~ ^[0-9.]+$ ]] && [ "$lhost" != "$HOST" ]; then break; fi
    _vargs=("${CURL_ARGS[@]}")
    [ "$lhost" != "$HOST" ] && _vargs+=(-H "Host: $lhost")
    _nbase="${lscheme}://${HOST}:${lport}${BASEPATH}"
    rc="$(curl "${_vargs[@]}" -o /dev/null -w '%{http_code}' "$_nbase")"
    [ "$rc" = "000" ] && break
    _progressed=0
    if [ "$SCHEME" != "$lscheme" ] || [ "$PORT" != "$lport" ] \
        || { [ -n "$lhost" ] && [ "$lhost" != "$HOST" ] && [ -z "$VH" ]; }; then
        _progressed=1
    fi
    SCHEME="$lscheme"; PORT="$lport"; BASE="$_nbase"; code="$rc"
    if [ "$lhost" != "$HOST" ] && [ -z "$VH" ]; then
        # adopt the vhost name only if the same request WITHOUT the Host
        # override still redirects — proof of name-based routing
        rc_ip="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "$_nbase")"
        case "$rc_ip" in 301|302|307|308)
            VH="$lhost"; _progressed=1
            warn "target routes by virtual host — using Host: $VH for all tools"
            warn "(equivalent /etc/hosts entry: '$HOST $VH')"
            if [ -z "$DOMAIN" ]; then
                # cohort.htb (2 labels) is itself the parent domain;
                # only strip the leading label for 3+ labels (www.foo.htb)
                if [ "$(awk -F. '{print NF}' <<< "$lhost")" -le 2 ]; then
                    DOMAIN="$lhost"
                else
                    DOMAIN="${lhost#*.}"
                fi
            fi
            ;;
        esac
    else
        info "redirect upgrade: switched to $SCHEME://$HOST:$PORT"
    fi
    [ "$_progressed" = 0 ] && break
done
# an explicit -H "Host: x" on the CLI means "scan that vhost"
for h in "${EXTRA_HDRS[@]:-}"; do
    case "$h" in Host:*) [ -z "$VH" ] && VH="${h#Host: }" ;;
    esac
done
CURL_ARGS+=(-H "Host: ${VH:-$HOST}")
# curl honors the FIRST Host header it is given, so requests that override
# Host (vhost fuzzing, Host: localhost bypass) need every -H Host:* removed
CURL_ARGS_NOHOST=()
_args=("${CURL_ARGS[@]}")
for ((i=0; i<${#_args[@]}; i++)); do
    if [ "${_args[$i]}" = "-H" ] && [[ "${_args[$((i+1))]:-}" == Host:* ]]; then
        ((i++)); continue
    fi
    CURL_ARGS_NOHOST+=("${_args[$i]}")
done
TOOL_HDRS+=("Host: ${VH:-$HOST}")
BASEDISPLAY="${SCHEME}://${VH:-$HOST}:${PORT}${BASEPATH}"

# per-tool header/proxy arguments, as arrays so quoting survives
HDR_FEROX=(); HDR_FFUF=(); HDR_GOB=(); HDR_WEB=(); HDR_NIKTO=()
PROXY_FEROX=(); PROXY_FFUF=(); PROXY_GOB=()
for h in "${TOOL_HDRS[@]:-}"; do
    [ -n "$h" ] || continue
    HDR_FEROX+=(-H "$h"); HDR_FFUF+=(-H "$h"); HDR_GOB+=(-H "$h")
    HDR_WEB+=(--header "$h"); HDR_NIKTO+=(-Add-header "$h")
done
if [ -n "$PROXY" ]; then
    PROXY_FEROX+=(-p "$PROXY"); PROXY_FFUF+=(-x "$PROXY"); PROXY_GOB+=(--proxy "$PROXY")
fi

# --------------------------------------------------- [1] fingerprint -------
banner "[1] FINGERPRINT — whatweb + headers"
if have whatweb; then
    whatweb -a 3 --no-errors "${HDR_WEB[@]}" \
        "${BASE%*/}" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' > "$OUT/whatweb.txt" || true
    head -c 600 "$OUT/whatweb.txt"; echo
else
    info "whatweb not installed — skipped"
fi
curl "${CURL_ARGS[@]}" -D - -o "$OUT/root.html" "$BASE" > "$OUT/root-headers.txt"
info "response headers saved to $OUT/root-headers.txt"
grep -iE '^(server|x-powered-by|x-aspnet|www-authenticate):' "$OUT/root-headers.txt" \
    | tr -d '\r' | sed 's/^/  /'
grep -ioP '<title>\K[^<]+' "$OUT/root.html" | head -1 | sed 's/^/  title: /'

# --- Next.js profile: image optimizer + buildId/manifest routes ---
if grep -qiE 'x-powered-by: next\.js|/_next/' \
        "$OUT/root-headers.txt" "$OUT/root.html" 2>/dev/null; then
    info "Next.js application detected"
    : > "$OUT/nextjs.txt"
    img_code="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' \
        "${BASE%*/}/_next/image?url=%2F&w=64&q=75")"
    case "$img_code" in
        200|400|403|500)
            warn "/_next/image optimizer responds (HTTP $img_code) — it fetches"
            warn "  arbitrary url= targets: test internal addresses (SSRF surface)"
            echo "image-optimizer: HTTP $img_code on /_next/image" >> "$OUT/nextjs.txt" ;;
        *) info "/_next/image not present ($img_code)" ;;
    esac
    bid="$(grep -oP '/_next/static/\K[A-Za-z0-9_-]{8,}(?=/)' "$OUT/root.html" \
        | head -1)"
    if [ -z "$bid" ]; then
        bid="$(sed -nE 's/^ETag: "([A-Za-z0-9_-]{6,})".*/\1/p' \
            "$OUT/root-headers.txt" | head -1)"
    fi
    if [ -n "$bid" ]; then
        for m in _buildManifest.js _ssgManifest.js; do
            murl="${BASE%*/}/_next/static/$bid/$m"
            msc="$(curl "${CURL_ARGS[@]}" -o "$OUT/$m" -w '%{http_code}' "$murl")"
            [ "$msc" = 200 ] || continue
            good "retrieved $murl"
            grep -oE '"/[a-zA-Z0-9_/-]{2,40}"' "$OUT/$m" | tr -d '"' | sort -u \
                | while read -r r; do
                    rsc="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' \
                        "${BASE%*/}$r")"
                    case "$rsc" in
                        200|301|302|307|308|401|403)
                            good "manifest route $r -> $rsc"
                            printf '%s\t%s\t%s\t(manifest)\n' "$rsc" "0" \
                                "${BASE%*/}$r" >> "$OUT/manifest-hits.txt" ;;
                    esac
                done
            break
        done
    fi
fi

# --- stack detection -> adaptive extensions + platform seeds ---
STACK="generic"
if grep -qiE 'server: .* (IIS|microsoft)|x-powered-by: .*asp\.net|x-aspnet-version|x-aspnetmvc-version' \
        "$OUT/root-headers.txt" 2>/dev/null; then
    STACK="iis"
    good "Windows/IIS target detected — arming asp/aspx/ashx/asmx/asax/axd extensions + IIS seeds"
elif grep -qiE 'x-powered-by: .*(servlet|jsp|jsf)|server: .*tomcat|server: .*jetty' \
        "$OUT/root-headers.txt" 2>/dev/null; then
    STACK="java"
    good "Java servlet target detected — arming jsp/jspx/do/action extensions + JAVA seeds"
fi

# ------------------------------------------------------------- [2] TLS ----
if [ "$SCHEME" = "https" ]; then
    banner "[2] TLS CERTIFICATE — openssl"
    openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null 2>/dev/null \
        | openssl x509 -noout -subject -issuer -dates -ext subjectAltName 2>/dev/null \
        | tr -d '\r' | sed 's/^/  /' | tee "$OUT/tls.txt"
    # cert CN/SAN is a vhost lead: use it for subdomain fuzzing when the
    # redirect-follow didn't already give us a domain
    if [ -z "$DOMAIN" ]; then
        cn="$(openssl s_client -connect "$HOST:$PORT" -servername "$HOST" </dev/null \
            2>/dev/null | openssl x509 -noout -subject 2>/dev/null \
            | sed -nE 's/.*CN[ =]+=+([^,]+).*/\1/p' | tr -d ' ')"
        case "$cn" in
            *.*)
                if ! [[ "$cn" =~ ^[0-9.]+$ ]]; then
                    if [ "$(awk -F. '{print NF}' <<< "$cn")" -le 2 ]; then
                        DOMAIN="$cn"
                    else
                        DOMAIN="${cn#*.}"
                    fi
                    info "vhost domain from cert CN: $DOMAIN"
                fi ;;
        esac
    fi
    grep -A1 "Subject Alternative Name" "$OUT/tls.txt" 2>/dev/null | grep -oE 'DNS:[a-z0-9.*-]+' \
        | cut -d: -f2 | sort -u | sed 's/^/  SAN: /'
fi

# ------------------------------------------------- [3] CORS / methods -----
banner "[3] CORS + HTTP METHODS — curl"
cors="$(curl "${CURL_ARGS[@]}" -D - -o /dev/null -H "Origin: https://evil-htb.example" \
    "$BASE" | tr -d '\r' | grep -i '^access-control-allow' )"
if [ -n "$cors" ]; then
    warn "CORS headers reflect origin:"
    printf '%s\n' "$cors" | sed 's/^/    /'
    printf '%s\n' "$cors" > "$OUT/cors.txt"
else
    info "no CORS reflection"
fi
allow="$(curl "${CURL_ARGS[@]}" -X OPTIONS -D - -o /dev/null "$BASE" | tr -d '\r' \
    | awk 'tolower($1)=="allow:"{print $0}')"
info "OPTIONS /: ${allow:-<no Allow header>}"
trace_code="$(curl "${CURL_ARGS[@]}" -X TRACE -o /dev/null -w '%{http_code}' "$BASE")"
[ "$trace_code" = 200 ] && warn "TRACE is enabled (XST)" \
    || info "TRACE not enabled ($trace_code)"
printf 'OPTIONS /: %s\nTRACE /: %s\n' "$allow" "$trace_code" > "$OUT/methods.txt"

# ------------------------------------------------ [4] robots / sitemap ----
banner "[4] ROBOTS.TXT / SITEMAP.XML — curl"
SEEDS=()
for f in robots.txt sitemap.xml; do
    body="$OUT/$f.body"
    sc="$(curl "${CURL_ARGS[@]}" -o "$body" -w '%{http_code}' "${BASE%*/}/$f")"
    [ "$sc" = 200 ] || continue
    good "$f (200, $(wc -c < "$body") bytes)"
    if [ "$f" = robots.txt ]; then
        grep -iE '^(disallow|allow|sitemap):' "$body" | tr -d '\r' \
            | tee "$OUT/robots-parsed.txt" | sed 's/^/    /'
        while IFS= read -r line; do
            val="$(printf '%s' "$line" | awk -F: '{print $2}' | tr -d ' ')"
            case "${val:-}" in
                /*) SEEDS+=("${val#/}") ;;
                http*) ;;
            esac
        done < <(grep -iE '^disallow:|^sitemap:' "$body" | tr -d '\r')
    else
        grep -oP '(?<=<loc>)[^<]+' "$body" | head -100 | tee -a "$OUT/sitemap-urls.txt" \
            | sed 's/^/    loc: /'
    fi
done
# probe robots disallow entries
for s in "${SEEDS[@]:-}"; do
    [ -z "$s" ] && continue
    sc="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "${BASE%*/}/$s")"
    printf '%s %s\n' "$sc" "$s" >> "$OUT/robots-hits.txt"
    warn "robots hint: /$s -> HTTP $sc"
done

# ------------------------------------------------- [5] content discovery --
# run_engine OUT URL [DEPTH_OVERRIDE] [COOKIE_JAR]
# retries once with throttled threads when the target refuses the burst
# (HTB boxes sometimes rate-limit after heavy scans)
run_engine() {
    _run_engine_once "$@"
    # adaptive throttle: mass 429s mean the box is rate-limiting — halve
    # thread count for the REST of this run and give it a cooling pause
    if grep -qaE "429" "$1.log" 2>/dev/null && [ ! -f "$OUT/.throttled" ]; then
        touch "$OUT/.throttled"
        warn "rate-limiting detected (429s) — halving threads for remaining scans"
        THREADS=$(( THREADS / 2 )); [ "$THREADS" -lt 5 ] && THREADS=5
        sleep 10
    fi
    if [ ! -s "$1" ] || grep -q "Could not connect" "$1.log" 2>/dev/null; then
        warn "engine failed against $2 — waiting 20s, retrying with 1/5 threads"
        sleep 20
        _t_saved="$THREADS"; THREADS=$(( THREADS / 5 )); [ "$THREADS" -lt 5 ] && THREADS=5
        _run_engine_once "$@"
        THREADS="$_t_saved"
    fi
}

_run_engine_once() {
    local out="$1" url="$2" rd="${3:-$DEPTH}" jar="${4:-}"
    local cookie_hdr=()
    if [ -n "$jar" ] && [ -s "$jar" ]; then
        local cv
        cv="$(awk '$7 != "" {printf "%s=%s; ", $6, $7}' "$jar" | sed 's/; $//')"
        [ -n "$cv" ] && cookie_hdr=(-H "Cookie: $cv")
    fi
    case "$ENGINE" in
        feroxbuster)
            feroxbuster -u "$url" -w "$WL" -x "$EXTENSIONS" -d "$rd" \
                -t "$THREADS" -k --auto-tune --extract-links \
                -s "200,204,301,302,307,308,401,403,405,500" \
                "${HDR_FEROX[@]}" "${cookie_hdr[@]}" "${PROXY_FEROX[@]}" \
                -o "$out" --no-state 2>&1 | tee "$out.log" | tail -8
            ;;
        ffuf)
            ffuf -u "${url%/}/FUZZ" -w "$WL" -recursion -recursion-depth "$rd" \
                -e "$EXTENSIONS" -ac -t "$THREADS" -k \
                "${HDR_FFUF[@]}" "${cookie_hdr[@]}" "${PROXY_FFUF[@]}" \
                -of json -o "$out" 2>&1 | tail -3
            ;;
        gobuster)
            gobuster dir -u "$url" -w "$WL" -x "$EXTENSIONS" -t "$THREADS" -k \
                -s "200,204,301,302,307,308,401,403,405,500" --no-error \
                "${HDR_GOB[@]}" "${cookie_hdr[@]}" "${PROXY_GOB[@]}" \
                -o "$out" 2>&1 | tail -3
            ;;
    esac
}

# parse a raw engine output file, appending normalized rows to $RESULTS
parse_engine() {
    case "$ENGINE" in
        feroxbuster)
            grep -E '^[0-9]{3}' "$1" | awk '{
                s = $5; sub(/c$/, "", s);
                loc = ($7 == "=>") ? "\t-> " $8 : "";
                print $1 "\t" s "\t" $6 loc
            }' >> "$RESULTS"
            ;;
        ffuf)
            python3 - "$1" >> "$RESULTS" <<'PYENG'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    for r in d.get("results", []):
        print(f'{r["status"]}\t{r["length"]}\t{r["url"]}')
except Exception as e:
    sys.stderr.write(str(e))
PYENG
            ;;
        gobuster)
            grep -oP 'Found: \K.*\(Status: \d+\).*' "$1" 2>/dev/null \
                | sed -E 's/(.*) \(Status: ([0-9]+)\) \[Size: ([0-9]+)\]/\2\t\3\t\1/' \
                >> "$RESULTS"
            ;;
    esac
}

if [ "$DO_CONTENT" = 1 ]; then
    case "$STACK" in
        iis)  EXTENSIONS="$EXTENSIONS,asp,aspx,asax,ashx,asmx,axd" ;;
        java) EXTENSIONS="$EXTENSIONS,jsp,jspx,do,action" ;;
    esac
    banner "[5] CONTENT DISCOVERY — $ENGINE (depth $DEPTH, extensions: $EXTENSIONS)"
    run_engine "$OUT/engine-main.txt" "$BASE"
fi

# normalize engine output -> results.txt (STATUS<TAB>SIZE<TAB>URL)
RESULTS="$OUT/results.txt"; : > "$RESULTS"
[ -f "$OUT/engine-main.txt" ] && parse_engine "$OUT/engine-main.txt"
[ -s "$OUT/manifest-hits.txt" ] && cat "$OUT/manifest-hits.txt" >> "$RESULTS"
TOTAL="$(wc -l < "$RESULTS")"
good "$TOTAL paths discovered (normalized to $OUT/results.txt)"
awk -F'\t' '{print $1}' "$RESULTS" | sort | uniq -c | sort -rn | sed 's/^/    /'

# drop strip-slash canonicalization redirects: servers like Next.js 308
# any "path/" back to "path" (the no-slash form is probed separately, so
# these rows carry no information). Add-slash redirects (nginx dirs) are
# kept — they are the classic directory signal.
awk -F'\t' '{
  if ($4 ~ /^-> /) {
    loc = substr($4, 4); url = $3
    lp = loc; sub(/^[a-z]+:\/\/[^/]+/, "", lp)
    up = url; sub(/^[a-z]+:\/\/[^/]+/, "", up)
    if (lp "/" == up) next
  }
  print
}' "$RESULTS" > "$RESULTS.tmp" && mv "$RESULTS.tmp" "$RESULTS"

# follow redirect targets (engines cannot follow cross-host Locations,
# e.g. https://box.htb/api/ while we probe by IP)
RESOLVE=()
[ -n "$VH" ] && RESOLVE=(--resolve "$VH:$PORT:$HOST")
n_followed=0; n_pruned=0
declare -A SEEN_TGT
while IFS=$'\t' read -r st sz url loc; do
    [ -z "$loc" ] && continue
    turl="${loc#-> }"
    thost="$(printf '%s' "$turl" | sed -E 's#^[a-z]+://([^/]+).*#\1#; s#:.*##')"
    case "$thost" in
        "$HOST"|"$VH") ;;
        *) continue ;;
    esac
    [ -n "${SEEN_TGT[$turl]:-}" ] && continue
    SEEN_TGT[$turl]=1
    read -r fsc fsz <<< "$(curl "${CURL_ARGS_NOHOST[@]}" "${RESOLVE[@]}" \
        -o /dev/null -w '%{http_code} %{size_download}' "$turl")"
    if [ "$fsc" = "000" ]; then
        # the Location's port may not match the listener we know; retry
        # against our base with the Location's path
        _tp="$(printf '%s' "$turl" | sed -E 's#^[a-z]+://[^/]+##')"
        read -r fsc fsz <<< "$(curl "${CURL_ARGS[@]}" -o /dev/null \
            -w '%{http_code} %{size_download}' "${BASE%*/}$_tp")"
    fi
    case "$fsc" in
        404|000)
            # dead target: the redirect itself is junk — prune its row
            awk -F'\t' -v u="$url" '$3 != u' "$RESULTS" > "$RESULTS.tmp" \
                && mv "$RESULTS.tmp" "$RESULTS"
            n_pruned=$((n_pruned+1)) ;;
        *)
            printf '%s\t%s\t%s\t(followed)\n' "$fsc" "$fsz" "$turl" >> "$RESULTS"
            info "redirect target $turl -> HTTP $fsc (${fsz}B)"
            n_followed=$((n_followed+1)) ;;
    esac
done < <(awk -F'\t' '$4 ~ /^-> /{print $1"\t"$2"\t"$3"\t"$4}' "$RESULTS")
[ $((n_followed + n_pruned)) -gt 0 ] \
    && info "redirect follow-up: $n_followed live target(s), $n_pruned dead redirect(s) pruned"

# recursion rescue: a redirect like http://IP/admin -> http://box.htb/admin/
# points the engine at another ORIGIN, so it never fuzzed inside /admin/.
# Re-run the engine scoped to that directory (IP + Host header) and merge.
RESCUED_PATHS=""
n_rescue=0
if [ "$DO_CONTENT" = 1 ] && [ -n "$VH" ] && [ "$DEPTH" -ge 1 ]; then
    while :; do
        [ "$n_rescue" -ge 5 ] && break
        # pending = live followed targets OR cross-origin redirect rows under
        # the vhost, not already rescued
        mapfile -t PENDING < <(awk -F'\t' -v vh="$VH" -v done_re="$RESCUED_PATHS" '
            {
                if ($4 == "(followed)") url = $3
                else if ($4 ~ /^-> /) url = substr($4, 4)
                else next
                if (url !~ "^https?://" vh "(:[0-9]+)?/") next
                if (url !~ /\/$/) next
                p = url; sub(/^https?:\/\/[^\/]+/, "", p)
                if (index(done_re, "|" p "|") > 0) next
                print p
            }' "$RESULTS" | sort -u)
        [ ${#PENDING[@]} -eq 0 ] && break
        [ "$n_rescue" -eq 0 ] && {
            warn "cross-origin directory redirects block engine recursion;"
            warn "running scoped re-scans of each directory (max 5):"
        }
        for dpath in "${PENDING[@]}"; do
            [ "$n_rescue" -ge 5 ] && break
            n_rescue=$((n_rescue+1))
            info "rescue scan $n_rescue: $dpath"
            # depth 1 here: the rescue queue itself handles nested
            # directories, so engine-internal recursion is redundant load
            _d_saved="$DEPTH"; DEPTH=1
            run_engine "$OUT/engine-rescue-$n_rescue.txt" \
                "${SCHEME}://${HOST}:${PORT}${dpath%/}/"
            DEPTH="$_d_saved"
            if [ -s "$OUT/engine-rescue-$n_rescue.txt" ]; then
                RESCUED_PATHS="$RESCUED_PATHS|$dpath|"
                parse_engine "$OUT/engine-rescue-$n_rescue.txt"
            else
                warn "rescue of $dpath produced nothing — not marking as done"
            fi
        done
    done
    if [ "$n_rescue" -gt 0 ]; then
        # dedupe exact rows, then demote soft-wildcard clusters (e.g. an
        # .htaccess that 403s every /admin/XXX.php — sizes vary with path
        # length, defeating the engine's auto-filter)
        sort -u -t$'\t' -k3,3 -k1,1 "$RESULTS" -o "$RESULTS"
        python3 - "$RESULTS" <<'PYSOFT'
import statistics, sys
rows = [ln.rstrip("\n").split("\t") for ln in open(sys.argv[1]) if ln.strip()]
keep, demoted = [], []
by_status = {}
for r in rows:
    by_status.setdefault(r[0], []).append(r)
for st, group in by_status.items():
    if len(group) >= 8:
        sizes = [int(r[1]) for r in group if r[1].isdigit()]
        if len(sizes) == len(group):
            med = statistics.median(sizes)
            band = [r for r in group if abs(int(r[1]) - med) <= 40]
            if len(band) >= 8:
                demoted.extend(band)
                keep.extend(r for r in group if r not in band)
                continue
    keep.extend(group)
open(sys.argv[1], "w").write("\n".join("\t".join(r) for r in keep) + "\n")
open(sys.argv[1] + ".soft-wildcard", "w").write(
    "\n".join("\t".join(r) for r in demoted) + "\n")
print(f"demoted {len(demoted)} soft-wildcard rows (see results.txt.soft-wildcard)")
PYSOFT
        good "recursion rescue: $n_rescue scoped scan(s), $(wc -l < "$RESULTS") rows in results.txt"
        awk -F'\t' '{print $1}' "$RESULTS" | sort | uniq -c | sort -rn | sed 's/^/    /'
    fi
fi

# auth realms of discovered 401s are recon gold (naming, product hints)
awk -F'\t' '$1==401{print $3}' "$RESULTS" | sort -u | head -8 \
    | while read -r aurl; do
        realm="$(curl "${CURL_ARGS[@]}" -D - -o /dev/null "$aurl" | tr -d '\r' \
            | awk 'tolower($1)=="www-authenticate:"{sub(/^[Ww][Ww][Ww]-[Aa]uthenticate: */,""); printf "%s ", $0}')"
        [ -n "$realm" ] || realm="(no WWW-Authenticate header)"
        warn "protected: $aurl -> $realm"
        printf '%s :: %s\n' "$aurl" "$realm" >> "$OUT/auth-realms.txt"
    done

# platform-specific seed files (high-value, cheap to probe directly)
IIS_SEEDS="web.config trace.axd elmah.axd Global.asax Global.asa \
iisstart.htm aspnet_client/ _vti_bin/ _vti_inf.html App_Data/ bin/ \
MSOffice/cltreq.asp"
JAVA_SEEDS="WEB-INF/web.xml META-INF/context.xml WEB-INF/classes/ \
WEB-INF/lib/ manager/html host-manager/html jmx-console/ web-console/"
case "$STACK" in
    iis)  PLAT_SEEDS="$IIS_SEEDS" ;;
    java) PLAT_SEEDS="$JAVA_SEEDS" ;;
    *)    PLAT_SEEDS="" ;;
esac
for s in $PLAT_SEEDS; do
    read -r psc psz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
        -w '%{http_code} %{size_download}' "${BASE%*/}/$s")
    case "$psc" in
        200|301|302|307|308|401|403)
            printf '%s\t%s\t%s/%s\t(seed)\n' "$psc" "$psz" "${BASE%*/}" "$s" \
                >> "$RESULTS"
            case "$psc" in
                200) warn "platform file /$s -> 200 (${psz}B)" ;;
                *)   info "platform file /$s -> $psc (exists, protected)" ;;
            esac ;;
    esac
done

# probe robots/sitemap seeds that the engine didn't report
while read -r s; do
    [ -z "$s" ] && continue
    grep -q "/$s\b" "$RESULTS" || printf 'seed\t0\t%s/%s\n' "${BASEDISPLAY%/}" "$s" >> "$RESULTS"
done < <(printf '%s\n' "${SEEDS[@]:-}")

# ------------------------------------------------------------ [6] vhosts --
if [ "$DO_VHOST" = 1 ] && have ffuf; then
    banner "[6] VIRTUAL HOST FUZZING — ffuf"
    [ -n "$DOMAIN" ] || DOMAIN="$HOST"
    NAMES="$OUT/vhost-names.txt"
    # curated high-value names are ALWAYS included: system lists (dnsmap)
    # are exhaustive but can miss obvious labels like "admin"
    printf '%s\n' admin api app auth backup beta blog cdn cms console \
        dashboard data db demo dev docs download files forum git help \
        home intranet jenkins lab legacy mail media monitor mx news old \
        panel portal private prod public remote restricted s3 shop site \
        staff staging static store support test testing vpn web wiki \
        www internal localhost > "$NAMES"
    [ -n "$VHOSTLIST" ] && cat "$VHOSTLIST" >> "$NAMES"
    sort -u "$NAMES" -o "$NAMES"
    RH="vhbase$(date +%s).invalid"
    curl "${CURL_ARGS_NOHOST[@]}" -H "Host: $RH" -o "$OUT/vh-baseline.body" "$BASE"
    base_size="$(wc -c < "$OUT/vh-baseline.body")"
    base_lines="$(wc -l < "$OUT/vh-baseline.body")"
    # strip the echoed hostname so canonicalization redirects normalize away
    base_sig="$(sed "s/$RH//g" "$OUT/vh-baseline.body" | md5sum | cut -d' ' -f1)"
    info "baseline (random Host): ${base_size}B ${base_lines}l — ffuf -fs/-fl + curl verification"
    ffuf -u "$BASE" -w "$NAMES" -H "Host: FUZZ.${DOMAIN}" \
        -fs "$base_size" -fl "$base_lines" \
        -mc 200,201,204,207,301,302,307,308,401,403 \
        -t "$THREADS" -k -of json -o "$OUT/vhosts.json" 2>&1 | tail -3
    python3 - "$OUT/vhosts.json" <<'PYEOF' > "$OUT/vhost-cands.txt"
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    for r in d.get("results", []):
        print(r.get("input", {}).get("FUZZ", "?"))
except Exception as e:
    sys.stderr.write(str(e))
PYEOF
    : > "$OUT/vhosts-found.txt"
    n_cands="$(wc -l < "$OUT/vhost-cands.txt")"
    [ "$n_cands" -gt 150 ] && warn "$n_cands ffuf hits — verifying first 150"
    head -150 "$OUT/vhost-cands.txt" | sort -u > "$OUT/vhost-cands.cap"
    while read -r cand; do
        [ -z "$cand" ] && continue
        host="${cand}.${DOMAIN}"
        curl "${CURL_ARGS_NOHOST[@]}" -H "Host: $host" -o "$OUT/vh-$$.body" "$BASE"
        sig="$(sed "s/$host//g" "$OUT/vh-$$.body" | md5sum | cut -d' ' -f1)"
        if [ "$sig" != "$base_sig" ]; then
            title="$(grep -ioP '<title>\K[^<]+' "$OUT/vh-$$.body" 2>/dev/null | head -1)"
            sz="$(wc -c < "$OUT/vh-$$.body")"
            printf 'vhost %s (%sB "%s")\n' "$host" "$sz" "$title"                 | tee -a "$OUT/vhosts-found.txt" | sed 's/^/  [+] /'
        fi
        rm -f "$OUT/vh-$$.body"
    done < "$OUT/vhost-cands.cap"
    if [ -s "$OUT/vhosts-found.txt" ]; then
        warn "add found vhosts to /etc/hosts and re-scan each"
        # auto-rescan: light content discovery on each found vhost (max 2),
        # merged into results with a (vhost-scan) marker
        n_vs=0
        grep -oE 'vhost [^ ]+' "$OUT/vhosts-found.txt" | awk '{print $2}' \
            | head -2 | while read -r vhn; do
                n_vs=$((n_vs+1))
                info "vhost re-scan $n_vs: $vhn"
                _t_saved="$THREADS"; THREADS=$(( THREADS / 2 )); \
                    [ "$THREADS" -lt 10 ] && THREADS=10
                run_engine "$OUT/engine-vhost-$n_vs.txt" "$BASE" 1
                THREADS="$_t_saved"
                if [ -s "$OUT/engine-vhost-$n_vs.txt" ]; then
                    _old_r="$RESULTS"; RESULTS="$OUT/vh-paths-$n_vs.txt"
                    : > "$RESULTS"
                    parse_engine "$OUT/engine-vhost-$n_vs.txt"
                    RESULTS="$_old_r"
                    sed "s#\t\$#\t(vhost-scan $vhn)#" \
                        "$OUT/vh-paths-$n_vs.txt" >> "$RESULTS"
                fi
            done
    else
        info "no vhost differences (after verification)"
    fi
fi

# ------------------------------------------------------- [7] UA diff -----
UAS=("curl/8.5.0" \
     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36" \
     "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \
     "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
     "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)" \
     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) Safari/604.1" \
     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)")
if [ "$DO_UA" = 1 ]; then
    banner "[7] USER-AGENT DIFFERENTIALS — curl"
    base_size="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{size_download}' "$BASE")"
    base_title="$(grep -ioP '<title>\K[^<]+' "$OUT/root.html" 2>/dev/null | head -1)"
    found=0
    for ua in "${UAS[@]}"; do
        sz="$(curl "${CURL_ARGS[@]}" -A "$ua" -o "$OUT/ua-$$.html" -w '%{size_download}' "$BASE")"
        t="$(grep -ioP '<title>\K[^<]+' "$OUT/ua-$$.html" 2>/dev/null | head -1)"
        if [ "$sz" != "$base_size" ] || [ "$t" != "$base_title" ]; then
            warn "UA '$ua': ${sz}B '$t' (baseline ${base_size}B '$base_title')"
            printf 'UA %s: %sB "%s"\n' "$ua" "$sz" "$t" >> "$OUT/ua-diff.txt"
            found=1
        fi
    done
    rm -f "$OUT/ua-$$.html"
    [ "$found" = 0 ] && info "all user agents get the same response"
fi

# --------------------------------------------------- [8] 403/401 bypass --
if [ "$DO_BYPASS" = 1 ]; then
    banner "[8] 403/401 BYPASS ATTEMPTS — curl"
    mapfile -t PROTECTED < <(awk -F'\t' '$1==403||$1==401{print $3}' "$RESULTS" | head -12)
    [ "$code" = 403 ] || [ "$code" = 401 ] && PROTECTED+=("$BASE")
    if [ ${#PROTECTED[@]} -eq 0 ]; then
        info "no 401/403 paths to attack"
    else
        # calibrate: many servers answer unknown paths with the homepage
        # (SPA fallback) — a 2xx that matches it is NOT a bypass
        read -r g_code g_size < <(curl "${CURL_ARGS[@]}" -o /dev/null \
            -w '%{http_code} %{size_download}' \
            "${BASE%*/}/htbgarbage$(date +%s)")
        root_size="$(wc -c < "$OUT/root.html" 2>/dev/null || echo 0)"
        info "calibration: garbage path -> $g_code/${g_size}B, homepage ${root_size}B"
        found=0
        for url in "${PROTECTED[@]}"; do
            orig="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "$url")"
            for trick in \
                "path:$url/" "path:$url/." "path:$url/..;/" "path:${url}..;/" \
                "path:$url%20" "path:$url." "path:${url}/;/anything" \
                "hdr:X-Forwarded-For: 127.0.0.1" "hdr:X-Original-URL: $url" \
                "hdr:X-Rewrite-URL: $url" "hdr:X-Forwarded-Host: localhost" \
                "hdr:Host: localhost"; do
                kind="${trick%%:*}"; spec="${trick#*:}"
                if [ "$kind" = path ]; then
                    read -r rc bsz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
                        -w '%{http_code} %{size_download}' "$spec")
                else
                    hdr_name="${spec%%:*}"
                    if [ "$hdr_name" = "Host" ]; then
                        read -r rc bsz < <(curl "${CURL_ARGS_NOHOST[@]}" -H "$spec" \
                            -o /dev/null -w '%{http_code} %{size_download}' "$url")
                    else
                        read -r rc bsz < <(curl "${CURL_ARGS[@]}" -H "$spec" \
                            -o /dev/null -w '%{http_code} %{size_download}' "$url")
                    fi
                fi
                case "$rc" in 200|201|204|207)
                    if [ "$bsz" = "$g_size" ] || [ "$bsz" = "$root_size" ]; then
                        info "200 via $trick but body matches SPA fallback (${bsz}B) — not a real bypass"
                    else
                        good "BYPASS $url ($orig -> $rc) via $trick (${bsz}B)"
                        printf '%s %s -> %s\n' "$url" "$orig" "$trick=$rc" \
                            >> "$OUT/bypass.txt"
                        found=1
                    fi ;;
                esac
            done
        done
        [ "$found" = 0 ] && info "no working bypass found"
    fi
fi

# --------------------------------------------- [9] comments + JS mining ---
banner "[9] HTML COMMENTS + JS MINING — curl + grep"
# comments from root and discovered index pages
{
    echo "$OUT/root.html"
    awk -F'\t' '$2>0 && $1<300 && $1>=200 {print $3}' "$RESULTS" | head -10
} | sort -u | while read -r u; do
    [ -f "$u" ] && f="$u" || { f="/tmp/hc-$$.html"; curl "${CURL_ARGS[@]}" -o "$f" "$u" 2>/dev/null; }
    [ -s "$f" ] || continue
    sed -n 's/.*<!--\(.*\)-->.*/\1/p' "$f" 2>/dev/null \
        | grep -iE 'todo|password|secret|hidden|admin|remove|note|key|token|debug' \
        | while read -r c; do
            warn "comment on $u: $(echo "$c" | head -c 140)"
            echo "$u :: $c" >> "$OUT/comments.txt"
          done
    [ -f "/tmp/hc-$$.html" ] && rm -f "/tmp/hc-$$.html"
done
[ -f "$OUT/comments.txt" ] || info "no interesting HTML comments"

# JS files from results + root page
if [ "$DO_JS" = 1 ]; then
    JSFILES="$(mktemp)"
    # base WITHOUT the default port, matching how the engines print URLs,
    # so the same file isn't fetched twice
    _JB="${SCHEME}://${HOST}"
    if { [ "$SCHEME" = http ] && [ "$PORT" != 80 ]; } \
        || { [ "$SCHEME" = https ] && [ "$PORT" != 443 ]; }; then
        _JB="$_JB:$PORT"
    fi
    awk -F'\t' '$3~/\.js$/{print $3}' "$RESULTS" > "$JSFILES"
    grep -oP '(?<=src=")[^"]*\.js' "$OUT/root.html" 2>/dev/null \
        | while read -r j; do
            case "$j" in
                http*) echo "$j" >> "$JSFILES" ;;
                /*) echo "${_JB}$j" >> "$JSFILES" ;;
                *) echo "${_JB}/$j" >> "$JSFILES" ;;
            esac
          done
    sort -u "$JSFILES" | head -30 | while read -r js; do
        curl "${CURL_ARGS[@]}" -o /tmp/js-$$.js "$js" 2>/dev/null || continue
        # grep -c counts matching LINES (minified JS is one line);
        # count occurrences instead
        n_obf="$(grep -oE '_0x[0-9a-f]{4,8}' /tmp/js-$$.js 2>/dev/null | wc -l)"
        if [ "${n_obf:-0}" -gt 100 ]; then
            warn "$js is OBFUSCATED ($n_obf mangled identifiers) — deobfuscate for analysis: npx webcrack $js"
            echo "$js :: obfuscated ($n_obf _0x identifiers) — deobfuscate (webcrack)" \
                >> "$OUT/js-secrets.txt"
            rm -f /tmp/js-$$.js
            continue
        fi
        grep -oiE "(api[_-]?key|apikey|secret|passw(or)?d|token|bearer)[\"']?[[:space:]]*[:=][[:space:]]*[\"'][A-Za-z0-9_@#%+/.,!-]{6,}[\"']" \
            /tmp/js-$$.js | sort -u | while read -r s; do
            warn "secret in $js: $(echo "$s" | head -c 100)"
            echo "$js :: $s" >> "$OUT/js-secrets.txt"
        done
        # hardcoded JWTs (eyJ... structured tokens) in client-side code
        grep -oE 'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(\.[A-Za-z0-9_-]{8,})?' \
            /tmp/js-$$.js | sort -u | while read -r jwt; do
            warn "JWT in $js: $(echo "$jwt" | head -c 60)..."
            echo "$js :: JWT $jwt" >> "$OUT/js-secrets.txt"
        done
        grep -oE '"(/[a-zA-Z0-9_./-]{3,40})"' /tmp/js-$$.js \
            | tr -d '"' | sort -u | head -20 | while read -r p; do
            case "$p" in *.css|*.png|*.jpg|*.svg|*.woff*|*.map) continue ;; esac
            sc="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "${BASE%*/}$p")"
            case "$sc" in 200|301|302|401|403)
                good "JS endpoint $p -> $sc"
                printf '%s\t%s\t%s\n' "$sc" "js" "${BASE%*/}$p" >> "$RESULTS" ;;
            esac
        done
        # source map exposure = full original source disclosure
        read -r msc msz < <(curl "${CURL_ARGS[@]}" -o /tmp/map-$$.body \
            -w '%{http_code} %{size_download}' "$js.map")
        case "$msc" in
            200|403)
                warn "SOURCE MAP exposed: $js.map ($msc, ${msz}B) - "
                warn "  original source incl. comments is recoverable"
                printf '%s\t%s\t%s.map\t(map)\n' "$msc" "$msz" "$js" \
                    >> "$RESULTS" ;;
        esac
        rm -f /tmp/js-$$.js /tmp/map-$$.body
    done
    rm -f "$JSFILES"
fi

# RSC flight payload (Next.js App Router): inline scripts carry the page's
# serialized React data — usernames, roles, hidden references
if grep -q "__next_f" "$OUT/root.html" 2>/dev/null; then
    python3 - "$OUT/root.html" "$OUT/flight-data.txt" <<'PYFLIGHT'
import re, sys
src = open(sys.argv[1], errors="replace").read()
inline = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', src, re.S)
blob = " ".join(inline)
chunks = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', blob)
joined = "".join(c.replace(chr(92)+chr(34), chr(34)).replace(chr(92)+chr(92), chr(92)) for c in chunks)
open(sys.argv[2], "w").write(joined)
PYFLIGHT
    if [ -s "$OUT/flight-data.txt" ]; then
        info "decoded $(wc -c < "$OUT/flight-data.txt")B of Next.js RSC flight data -> flight-data.txt"
        grep -oiE '(password|secret|token|api[_-]?key|internal|admin|flag)[^,}]{0,50}' \
            "$OUT/flight-data.txt" | sort -u | while read -r s; do
            warn "flight data: $(echo "$s" | head -c 100)"
            echo "flight :: $s" >> "$OUT/js-secrets.txt"
        done
        # human-readable words are username/role candidates on HTB
        grep -oE '[A-Z][a-z]+ [A-Z][a-z]+' "$OUT/flight-data.txt" | sort -u \
            | head -15 > "$OUT/name-candidates.txt"
        [ -s "$OUT/name-candidates.txt" ] \
            && info "name candidates: $(paste -sd, "$OUT/name-candidates.txt" | head -c 200)"
    fi
fi

# ------------------------------------- [10] API documentation discovery ----
banner "[10] API DOCS DISCOVERY — seeds + openapi parsing + base-path walk"
declare -A API_SEEN
api_probe() {  # $1 = path without leading slash; records into results.txt
    local p="${1#/}"
    [ -z "$p" ] && return
    [ -n "${API_SEEN[$p]:-}" ] && return
    API_SEEN[$p]=1
    grep -qE "/$p(\t|\$)" "$RESULTS" && return
    local sc sz
    read -r sc sz < <(curl "${CURL_ARGS[@]}" -o /tmp/api-$$.body \
        -w '%{http_code} %{size_download}' "${BASE%*/}/$p")
    case "$sc" in
        200|301|302|307|308|401|403) ;;
        *) rm -f /tmp/api-$$.body; return ;;
    esac
    printf '%s\t%s\t%s/%s\t(api-doc)\n' "$sc" "$sz" "${BASE%*/}" "$p" \
        >> "$RESULTS"
    if [ "$sc" = 200 ] && head -c 4096 /tmp/api-$$.body \
            | grep -qE '"(openapi|swagger)"[[:space:]]*:|"paths"[[:space:]]*:'; then
        good "API SPEC at /$p — extracting endpoints"
        python3 - /tmp/api-$$.body >> "$OUT/api-endpoints.txt" <<'PYAPI'
import json, sys, re
try:
    d = json.load(open(sys.argv[1], errors="replace"))
    for path in d.get("paths", {}):
        base = re.sub(r"\{[^}]*\}", "", path).rstrip("/")
        print(base or "/")
except Exception:
    pass
PYAPI
    elif [ "$sc" = 200 ] && head -c 4096 /tmp/api-$$.body \
            | grep -qiE 'swagger-ui|redoc|graphiql|apidoc|api documentation'; then
        good "API documentation UI at /$p (${sz}B)"
    else
        info "/$p -> $sc (${sz}B)"
    fi
    rm -f /tmp/api-$$.body
}

# 1) curated documentation seeds
for s in api api/ api/v1 api/v2 api/v3 swagger swagger/ swagger/index.html \
    swagger-ui swagger-ui/ swagger-ui/index.html swagger-ui.html swagger.json \
    openapi.json openapi.yaml api-docs api-docs/ api/swagger.json \
    api/openapi.json api/v1/swagger.json api/v1/openapi.json graphiql graphql \
    docs docs/ redoc actuator actuator/mappings v1 v2 v3 api/schema; do
    api_probe "$s"
done

# 2) base-path investigation: for every discovered path, probe each
#    ancestor directory (resource /api/swagger/v1/users/123 -> probe
#    /api/swagger/v1/users, /api/swagger/v1, /api/swagger, /api)
mapfile -t ALL_PATHS < <(awk -F'\t' '{print $3}' "$RESULTS" \
    | sed -E 's#^[a-z]+://[^/]+##' | grep -E '^/.+' | sort -u)
for ap in "${ALL_PATHS[@]}"; do
    case "$ap" in
        */) d="${ap%/}" ;;
        *.*) d="$(dirname "$ap")" ;;
        *)   d="$ap" ;;
    esac
    while [ "$d" != "/" ] && [ -n "$d" ]; do
        api_probe "$d"
        api_probe "$d/"
        d="${d%/*}"
    done
done

# 2b) parse spec files the ENGINE already discovered (api_probe skips
#     known paths, so without this a ferox-found openapi.json is never read)
grep -E "openapi\.json|swagger\.json" "$RESULTS" 2>/dev/null \
    | awk -F'\t' '{print $3}' | sort -u | while read -r surl; do
    curl "${CURL_ARGS[@]}" -o /tmp/spec-$$.json "$surl" 2>/dev/null || continue
    if head -c 4096 /tmp/spec-$$.json \
            | grep -qE '"(openapi|swagger)"[[:space:]]*:|"paths"[[:space:]]*:'; then
        good "API SPEC already discovered at $surl - extracting endpoints"
        python3 - /tmp/spec-$$.json >> "$OUT/api-endpoints.txt" <<'PYSPEC'
import json, sys, re
try:
    d = json.load(open(sys.argv[1], errors="replace"))
    for path in d.get("paths", {}):
        base = re.sub(r"\{[^}]*\}", "", path).rstrip("/")
        print(base or "/")
except Exception:
    pass
PYSPEC
    fi
    rm -f /tmp/spec-$$.json
done

# 3) probe every endpoint extracted from API specs
if [ -s "$OUT/api-endpoints.txt" ]; then
    n_eps=$(sort -u "$OUT/api-endpoints.txt" | wc -l)
    good "$n_eps endpoint(s) extracted from API spec(s) — probing"
    sort -u "$OUT/api-endpoints.txt" | head -60 | while read -r ep; do
        ep="${ep#/}"
        [ -n "$ep" ] || continue
        sc="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "${BASE%*/}/$ep")"
        case "$sc" in
            200|301|302|307|308|401|403)
                sz="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{size_download}' \
                    "${BASE%*/}/$ep")"
                printf '%s\t%s\t%s/%s\t(api)\n' "$sc" "$sz" "${BASE%*/}" "$ep" \
                    >> "$RESULTS"
                good "API endpoint /$ep -> $sc (${sz}B)" ;;
        esac
    done
else
    info "no API documentation found"
fi

# GraphQL introspection: an open __schema dumps the whole API shape
for gq in graphql graphiql api/graphql graphql/ v1/graphql; do
    gsc="$(curl "${CURL_ARGS[@]}" -o /tmp/gq-$$.body \
        -w '%{http_code}' -X POST -H 'Content-Type: application/json' \
        --data '{"query":"{ __schema { queryType { name } } }"}' \
        "${BASE%*/}/$gq")"
    if [ "$gsc" = 200 ] && grep -qiE 'queryType|__schema' /tmp/gq-$$.body; then
        warn "GRAPHQL INTROSPECTION ENABLED at /$gq - full schema is dumpable"
        printf '200\t0\t%s/%s\t(graphql)\n' "${BASE%*/}" "$gq" >> "$RESULTS"
        echo "graphql: /$gq introspection enabled" >> "$OUT/js-secrets.txt"
    elif [ "$gsc" = 200 ]; then
        info "GraphQL at /$gq but introspection is disabled (good)"
    fi
    rm -f /tmp/gq-$$.body
done

# --------------------------------- [9a] hidden parameter discovery --------
banner "[9a] PARAMETER DISCOVERY - hidden params on live endpoints"
P_NAMES="debug admin id user test cmd exec source file page sort filter q search"
P_VALS="1 true test"
mapfile -t P_TARGETS < <(awk -F'\t' '$1==200 {print $3}' "$RESULTS" \
    | grep -E '/(api|graphql|search|query|items|users|orders|transfer|accounts|lib)' \
    | sort -u | head -8)
if [ ${#P_TARGETS[@]} -eq 0 ]; then
    info "no API-ish endpoints for parameter probing"
else
    : > "$OUT/params-found.txt"
    for pt in "${P_TARGETS[@]}"; do
        read -r b_code b_size < <(curl "${CURL_ARGS[@]}" -o /dev/null \
            -w '%{http_code} %{size_download}' "$pt")
        for pn in $P_NAMES; do
            for pv in $P_VALS; do
                read -r p_code p_size < <(curl "${CURL_ARGS[@]}" \
                    -o "$OUT/p-$$.body" \
                    -w '%{http_code} %{size_download}' "$pt?$pn=$pv")
                if { [ "$p_code" != "$b_code" ] || [ "$p_size" != "$b_size" ]; } \
                        && [ "$p_code" != 404 ] && [ "$p_size" != 0 ]; then
                    good "live parameter: $pt?$pn=$pv ($b_code/${b_size}B -> $p_code/${p_size}B)"
                    printf '%s?%s=%s\t%s->%s\n' "$pt" "$pn" "$pv" \
                        "$b_code" "$p_code" >> "$OUT/params-found.txt"
                    break 2
                fi
                rm -f "$OUT/p-$$.body"
            done
        done
        rm -f "$OUT/p-$$.body"
    done
    [ -s "$OUT/params-found.txt" ] \
        || info "no hidden parameters changed responses"
fi

# object-reference sweep: collection endpoints often expose /1 /2 ... IDs
mapfile -t IDOR_T < <(awk -F'\t' '$1==200 {print $3}' "$RESULTS" \
    | sed -E 's#/$##' \
    | grep -E '/(users|orders|accounts|items|invoices|messages|clients|docs)$' \
    | sort -u | head -6)
if [ ${#IDOR_T[@]} -gt 0 ]; then
    : > "$OUT/idor-found.txt"
    for c in "${IDOR_T[@]}"; do
        for i in 1 2 3 4 5; do
            read -r irc isz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
                -w '%{http_code} %{size_download}' "$c/$i")
            if [ "$irc" = 200 ] && [ "$isz" -gt 2 ]; then
                good "OBJECT ACCESSIBLE: $c/$i (200, ${isz}B) - IDOR candidate"
                printf '200\t%s\t%s/%s\t(idor)\n' "$isz" "$c" "$i" >> "$RESULTS"
                printf '%s/%s\t200 (%sB)\n' "$c" "$i" "$isz" \
                    >> "$OUT/idor-found.txt"
            fi
        done
    done
    [ -s "$OUT/idor-found.txt" ] \
        || info "no directly accessible objects found"
fi

# ------------------------------ [9b] authenticated scan + content diff ----
if [ -n "$AUTH_USER" ] && [ -n "$AUTH_PASS" ]; then
    banner "[9b] AUTHENTICATED SCAN - login + content diff"
    # pick the login endpoint: explicit flag or first discovered candidate
    LOGIN_URL="$AUTH_LOGIN"
    if [ -z "$LOGIN_URL" ]; then
        cand="$(awk -F'\t' '$3 ~ /(login|signin|sign-in|wp-login)/ {print $3}' \
            "$RESULTS" | head -1)"
        [ -n "$cand" ] && LOGIN_URL="$cand"
    fi
    if [ -z "$LOGIN_URL" ]; then
        warn "credentials given but no login endpoint discovered - pass --auth-login URL"
    else
        info "attempting login at $LOGIN_URL"
        : > "$OUT/auth.cookies"
        for uf in user username email log; do
            for pf in pass password pwd; do
                curl "${CURL_ARGS[@]}" -c "$OUT/auth.cookies" \
                    -d "$uf=$AUTH_USER&$pf=$AUTH_PASS" \
                    -o "$OUT/auth-post.body" "$LOGIN_URL"
                # success signal: a session-looking cookie was set
                if grep -qiE "session|auth|token|sid" "$OUT/auth.cookies" 2>/dev/null; then
                    good "login succeeded (user=$uf pass=$pf) - session captured"
                    printf 'login: POST %s (%s=%s %s=**)\n' "$LOGIN_URL" \
                        "$uf" "$AUTH_USER" "$pf" > "$OUT/auth-creds.txt"
                    break 2
                fi
            done
        done
        if grep -qiE "session|auth|token|sid" "$OUT/auth.cookies" 2>/dev/null; then
            # authenticated re-scan of the base with the session
            AUTH_ARGS=("${CURL_ARGS[@]}" -b "$OUT/auth.cookies")
            acode="$(curl "${AUTH_ARGS[@]}" -o /dev/null \
                -w '%{http_code}' "$BASE")"
            info "authenticated root probe: HTTP $acode"
            printf '%s\t%s\t%s\t(auth-root)\n' "$acode" "0" "$BASE" >> "$RESULTS"
            # compare a quick protected-path probe with/without session
            mapfile -t GATED < <(awk -F'\t' '$1==401||$1==403{print $3}' \
                "$RESULTS" | sort -u | head -10)
            for g in "${GATED[@]}"; do
                ac="$(curl "${AUTH_ARGS[@]}" -o "$OUT/auth-$$.body" \
                    -w '%{http_code}' "$g")"
                if [ "$ac" = 200 ]; then
                    asz="$(wc -c < "$OUT/auth-$$.body")"
                    good "AUTH-ONLY PATH: $g opens with session (200, ${asz}B)"
                    printf '200\t%s\t%s\t(auth-only)\n' "$asz" "$g" >> "$RESULTS"
                fi
                rm -f "$OUT/auth-$$.body"
            done
            # deep discovery with the session (small list, depth 1)
            run_engine "$OUT/engine-auth.txt" "$BASE" 1 "$OUT/auth.cookies"
            if [ -s "$OUT/engine-auth.txt" ]; then
                _old_r="$RESULTS"; RESULTS="$OUT/auth-paths.txt"; : > "$RESULTS"
                parse_engine "$OUT/engine-auth.txt"
                RESULTS="$_old_r"
                comm -13 <(awk -F'\t' '{print $3}' "$RESULTS" | sort -u) \
                    <(awk -F'\t' '{print $3}' "$OUT/auth-paths.txt" | sort -u) \
                    > "$OUT/auth-new-paths.txt"
                n_new="$(wc -l < "$OUT/auth-new-paths.txt")"
                good "authenticated discovery: $n_new path(s) not visible logged-out"
                while read -r np; do
                    printf 'auth-only\t0\t%s\n' "$np" >> "$RESULTS"
                    warn "auth-only path: $np"
                done < "$OUT/auth-new-paths.txt"
            fi
        else
            warn "login did not yield a session cookie - check credentials/form"
        fi
    fi
fi

# scan diff against a previous run
if [ -n "$DIFF_DIR" ] && [ -f "$DIFF_DIR/results.txt" ]; then
    banner "[9c] SCAN DIFF vs $DIFF_DIR"
    comm -13 <(awk -F'\t' '{print $3}' "$DIFF_DIR/results.txt" | sort -u) \
        <(awk -F'\t' '{print $3}' "$RESULTS" | sort -u) \
        > "$OUT/diff-new-paths.txt"
    comm -23 <(awk -F'\t' '{print $3}' "$DIFF_DIR/results.txt" | sort -u) \
        <(awk -F'\t' '{print $3}' "$RESULTS" | sort -u) \
        > "$OUT/diff-gone-paths.txt"
    good "$(wc -l < "$OUT/diff-new-paths.txt") new, $(wc -l < "$OUT/diff-gone-paths.txt") gone (diff-new-paths.txt / diff-gone-paths.txt)"
    head -10 "$OUT/diff-new-paths.txt" | while read -r np; do
        [ -n "$np" ] && warn "NEW since last scan: $np"
    done
fi

# -------------------------- [9e] basic-auth default credential spray ------
if [ "$DEFAULT_CREDS" = 1 ] && [ -s "$OUT/auth-realms.txt" ]; then
    banner "[9e] DEFAULT CREDENTIAL SPRAY - Basic auth realms"
    : > "$OUT/default-creds-hit.txt"
    awk -F' :: ' '{print $1}' "$OUT/auth-realms.txt" | sort -u | head -5 \
        | while read -r burl; do
            hit=""
            for pair in admin:admin admin:password admin:admin123 \
                root:root test:test guest:guest user:user admin:123456; do
                u="${pair%%:*}"; pw="${pair#*:}"
                rc="$(curl "${CURL_ARGS[@]}" -u "$u:$pw" \
                    -o /dev/null -w '%{http_code}' "$burl")"
                if [ "$rc" = 200 ]; then
                    good "DEFAULT CREDS WORK: $burl with $u:$pw"
                    printf '%s\t%s:%s\n' "$burl" "$u" "$pw" \
                        >> "$OUT/default-creds-hit.txt"
                    hit=1; break
                fi
            done
            [ -z "$hit" ] && info "no default credentials on $burl"
        done
fi

# -------------------------------------- [10a] deep content profile --------
banner "[10a] DEEP CONTENT PROFILE - backups, source maps, CMS, emails"
# calibration: a .bak that is byte-identical to the homepage is an SPA
# fallback, not a backup file
read -r bk_g_code bk_g_size < <(curl "${CURL_ARGS[@]}" -o /dev/null \
    -w '%{http_code} %{size_download}' "${BASE%*/}/bkcalib$(date +%s)")
bk_root_size="$(wc -c < "$OUT/root.html" 2>/dev/null || echo 0)"
# backup-suffix probe: for each discovered code/text file, try the classic
# editor/backup suffixes (config.php -> config.php.bak ...)
awk -F'\t' '$3 ~ /\.(php|html?|js|json|txt|conf|ini|ya?ml|xml)(\t|$| ->)/ {print $3}' \
    "$RESULTS" | sed 's/[[:space:]]*$//' | sort -u | head -20 \
    | while read -r f; do
        for sfx in ".bak" ".old" "~" ".orig"; do
            read -r bsc bsz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
                -w '%{http_code} %{size_download}' "$f$sfx")
            # same-extension garbage: wildcard APIs answer anything with
            # a uniform body — only flag if the .bak differs from BOTH the
            # bare garbage and the same-suffix garbage
            read -r _ _bk_g2 < <(curl "${CURL_ARGS[@]}" -o /dev/null \
                -w '%{http_code} %{size_download}' \
                "${BASE%*/}/bkcalib$(date +%s)$sfx")
            case "$bsc" in
                200)
                    if [ "$bsz" != "$bk_g_size" ] && [ "$bsz" != "$bk_root_size" ] \
                            && [ "$bsz" != "$_bk_g2" ]; then
                        warn "BACKUP FILE: $f$sfx -> $bsc (${bsz}B)"
                        printf '%s\t%s\t%s%s\t(backup)\n' "$bsc" "$bsz" "$f" \
                            "$sfx" >> "$RESULTS"
                    fi ;;
                403)
                    warn "BACKUP FILE (protected): $f$sfx -> 403"
                    printf '403\t%s\t%s%s\t(backup)\n' "$bsz" "$f" \
                        "$sfx" >> "$RESULTS" ;;
            esac
        done
    done

# CMS profile (WordPress): user enumeration via REST is the classic HTB find
if grep -qiE 'wp-content|wp-json|wp-login|wordpress' \
        "$RESULTS" "$OUT/whatweb.txt" "$OUT/root.html" 2>/dev/null; then
    good "WordPress markers detected - running CMS profile"
    curl "${CURL_ARGS[@]}" -o /tmp/wpu-$$.json "${BASE%*/}/wp-json/wp/v2/users"
    if head -c 4096 /tmp/wpu-$$.json | grep -q '"slug"'; then
        python3 - /tmp/wpu-$$.json <<'PYWP' | tee -a "$OUT/name-candidates.txt" \
            | while read -r u; do warn "WordPress user: $u"; done
import json, sys
try:
    for u in json.load(open(sys.argv[1], errors="replace")):
        print(u.get("slug", ""))
except Exception:
    pass
PYWP
        printf '200\t0\t%s/wp-json/wp/v2/users\t(cms)\n' \
            "${BASE%*/}" >> "$RESULTS"
    fi
    rm -f /tmp/wpu-$$.json
    for cp in wp-content/uploads/ readme.html wp-config.php.bak xmlrpc.php \
        wp-login.php wp-content/debug.log; do
        read -r csc csz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
            -w '%{http_code} %{size_download}' "${BASE%*/}/$cp")
        case "$csc" in
            200|301|302|401|403)
                printf '%s\t%s\t%s/%s\t(cms)\n' "$csc" "$csz" "${BASE%*/}" \
                    "$cp" >> "$RESULTS"
                warn "WordPress path /$cp -> $csc" ;;
        esac
    done
fi

# email harvesting: addresses double as usernames on HTB
{
    cat "$OUT/root.html" 2>/dev/null
    awk -F'\t' '$1==200 && $3 ~ /\.(html?|aspx|php)(\/)?(\t|$)/ {print $3}' \
        "$RESULTS" | sort -u | head -5 | while read -r hurl; do
            curl "${CURL_ARGS[@]}" -s -m 10 "$hurl" 2>/dev/null
        done
} | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' | sort -u \
    | tee -a "$OUT/name-candidates.txt" | while read -r e; do
        info "email found: $e (username candidate)"
    done

# ------------------------------------------ [10b] HTTP method audit ------
banner "[10b] HTTP METHOD AUDIT — OPTIONS sweep + verb tampering"
RISKY_RE='PUT|DELETE|PATCH|TRACE|TRACK|CONNECT|DEBUG|PROPFIND|PROPPATCH|MKCOL|COPY|MOVE|LOCK|UNLOCK'
: > "$OUT/methods-matrix.txt"
: > "$OUT/risky-methods.txt"
# every discovered endpoint, 401/403 paths first (most interesting for
# bypass), then everything else
# 401/403 paths first, then high-value endpoints (api/admin/...), then the
# rest — extension-variant rows (.bak/.old/...) sort last so they cannot
# crowd out the interesting endpoints
mapfile -t M_PATHS < <(
    {
        awk -F'\t' '$1==401||$1==403{print $3}' "$RESULTS" \
            | sed -E 's#^[a-z]+://[^/]+##'
        awk -F'\t' '$1!=401&&$1!=403{print $3}' "$RESULTS" \
            | sed -E 's#^[a-z]+://[^/]+##' \
            | grep -E '(api|admin|login|graphql|actuator|upload|backup|config|users|orders|transfer|manage)' \
            | sort -u | head -20
        awk -F'\t' '$1!=401&&$1!=403{print $3}' "$RESULTS" \
            | sed -E 's#^[a-z]+://[^/]+##' \
            | grep -vE '/[^/]*\.[a-zA-Z0-9]+(\.|$|\?)' | sort -u | head -20
    } | awk 'NF' | sort -u | head -50)
for mp in "${M_PATHS[@]}"; do
    allow="$(curl "${CURL_ARGS[@]}" -X OPTIONS -D - -o /dev/null \
        "${BASE%*/}$mp" | tr -d '\r' \
        | awk 'tolower($1)=="allow:"{sub(/^[Aa]llow: */,""); printf "%s ", $0}')"
    allow="${allow% }"
    [ -z "$allow" ] && continue
    printf '%s\t%s\n' "$mp" "$allow" >> "$OUT/methods-matrix.txt"
    risky="$(printf '%s' "$allow" | tr ',' '\n' | tr -d ' ' \
        | grep -xE "$RISKY_RE" | paste -sd, -)"
    if [ -n "$risky" ]; then
        warn "RISKY methods allowed on $mp: $risky"
        printf '%s\t%s\n' "$mp" "$risky" >> "$OUT/risky-methods.txt"
        grep -qE 'PROPFIND|MKCOL|MOVE|COPY|LOCK' <<< "$risky" \
            && warn "  WebDAV verbs present — test with davtest/cadaver" \
            && { have davtest && [ "$ACTIVE_METHODS" = 1 ] && {
                info "running davtest against $mp"
                davtest -url "${BASE%*/}$mp" 2>/dev/null \
                    | grep -E "SUCCEED|FAIL" | head -6 \
                    | tee "$OUT/davtest.txt" | sed 's/^/      /'
            } ; }
        grep -q '^PUT' <<< "$risky" \
            && warn "  PUT allowed — webshell upload candidate (see --active-methods)"
    fi
done
info "$(wc -l < "$OUT/methods-matrix.txt") endpoint(s) expose Allow headers (methods-matrix.txt)"

# verb tampering: OPTIONS often lies — filters match known verbs only.
# Try non-standard verbs, case swaps, and method-override headers against
# protected paths, with SPA-fallback calibration so homepage echoes
# don't register as bypasses.
mapfile -t T_PATHS < <(awk -F'\t' '$1==401||$1==403{print $3}' "$RESULTS" \
    | sed -E 's#^[a-z]+://[^/]+##; s#/$##' | sort -u | head -12)
if [ ${#T_PATHS[@]} -gt 0 ]; then
    read -r g_code g_size < <(curl "${CURL_ARGS[@]}" -o /dev/null \
        -w '%{http_code} %{size_download}' "${BASE%*/}/htbgarbage$(date +%s)")
    root_size="$(wc -c < "$OUT/root.html" 2>/dev/null || echo 0)"
    for tp in "${T_PATHS[@]}"; do
        turl="${BASE%*/}$tp"
        orig="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "$turl")"
        for verb in FOO pUt GeT HEAD POST; do
            read -r rc bsz < <(curl "${CURL_ARGS[@]}" -X "$verb" -o /dev/null \
                -w '%{http_code} %{size_download}' "$turl")
            case "$rc" in
                200|201|204|207)
                    if [ "$bsz" != "$g_size" ] && [ "$bsz" != "$root_size" ]; then
                        warn "VERB TAMPER: $tp ($orig -> $rc) via X $verb (${bsz}B)"
                        printf '%s %s X %s -> %s\n' "$tp" "$orig" "$verb" "$rc" \
                            >> "$OUT/bypass.txt"
                    fi ;;
            esac
        done
        for hdr in "X-HTTP-Method-Override: PUT" "X-HTTP-Method-Override: DELETE" \
            "X-HTTP-Method: PUT" "X-Method-Override: PATCH"; do
            read -r rc bsz < <(curl "${CURL_ARGS[@]}" -H "$hdr" -o /dev/null \
                -w '%{http_code} %{size_download}' "$turl")
            case "$rc" in
                200|201|204|207)
                    if [ "$bsz" != "$g_size" ] && [ "$bsz" != "$root_size" ]; then
                        warn "VERB TAMPER: $tp ($orig -> $rc) via $hdr (${bsz}B)"
                        printf '%s %s %s -> %s\n' "$tp" "$orig" "$hdr" "$rc" \
                            >> "$OUT/bypass.txt"
                    fi ;;
            esac
        done
    done
fi

# opt-in active verification: PUT a marker file, confirm writability,
# clean it up with DELETE (modifies the target — off by default)
if [ "$ACTIVE_METHODS" = 1 ]; then
    banner "[10b+] ACTIVE METHOD PROBES — PUT/TRACE verification"
    marker="/htb-methodprobe-$(date +%s).txt"
    for tp in $(head -5 "$OUT/risky-methods.txt" 2>/dev/null | cut -f1); do
        rc="$(curl "${CURL_ARGS[@]}" -X PUT --data-binary "probe" \
            -o /dev/null -w '%{http_code}' "${BASE%*/}$tp$marker")"
        case "$rc" in
            200|201|204|205)
                good "PUT CONFIRMED on $tp (HTTP $rc) — directory is writable"
                drc="$(curl "${CURL_ARGS[@]}" -X DELETE -o /dev/null \
                    -w '%{http_code}' "${BASE%*/}$tp$marker")"
                info "cleanup DELETE of marker -> $drc" ;;
            *) info "PUT on $tp -> $rc (not writable)" ;;
        esac
    done
    trc="$(curl "${CURL_ARGS[@]}" -X TRACE -D - -o /dev/null "${BASE%*/}/" \
        | tr -d '\r')"
    grep -qi "^TRACE /" <<< "$trc" \
        && warn "TRACE reflects the request (cross-site tracing possible)"
fi

# ---------------------------------- [10c] HTTP security posture -----------
banner "[10c] HTTP SECURITY POSTURE - cookies + headers"
sc_all="$(curl "${CURL_ARGS[@]}" -D - -o /dev/null "$BASE" | tr -d '\r')"
: > "$OUT/cookie-flags.txt"; : > "$OUT/missing-headers.txt"
printf '%s\n' "$sc_all" | grep -i '^set-cookie:' | while read -r c; do
    missing=""
    grep -qi 'secure' <<< "$c" || missing="$missing Secure"
    grep -qi 'httponly' <<< "$c" || missing="$missing HttpOnly"
    grep -qi 'samesite' <<< "$c" || missing="$missing SameSite"
    if [ -n "$missing" ]; then
        warn "cookie missing flags:$missing — ${c:0:60}"
        printf '%s\tmissing:%s\n' "$c" "$missing" >> "$OUT/cookie-flags.txt"
    fi
done
for h in Strict-Transport-Security Content-Security-Policy \
         X-Frame-Options X-Content-Type-Options Referrer-Policy; do
    if ! grep -qi "^$h:" <<< "$sc_all"; then
        # HSTS is meaningless over plain HTTP
        [ "$h" = "Strict-Transport-Security" ] && [ "$SCHEME" != https ] \
            && continue
        warn "security header missing: $h"
        echo "$h" >> "$OUT/missing-headers.txt"
    fi
done
[ -s "$OUT/cookie-flags.txt" ] || info "cookies at root: all flags present (or none set)"
# session cookies often appear on app endpoints, not the root — sweep them
awk -F'\t' '$1==200 {print $3}' "$RESULTS" | sort -u | head -5 \
    | while read -r curl2; do
        curl "${CURL_ARGS[@]}" -D - -o /dev/null "$curl2" 2>/dev/null \
            | tr -d '\r' | grep -i '^set-cookie:' | while read -r c; do
            missing=""
            grep -qi 'secure' <<< "$c" || missing="$missing Secure"
            grep -qi 'httponly' <<< "$c" || missing="$missing HttpOnly"
            grep -qi 'samesite' <<< "$c" || missing="$missing SameSite"
            if [ -n "$missing" ]; then
                warn "cookie missing flags:$missing — ${c:0:60}"
                printf '%s\tmissing:%s\n' "$c" "$missing" \
                    >> "$OUT/cookie-flags.txt"
            fi
        done
    done
[ -s "$OUT/missing-headers.txt" ] \
    || info "all standard security headers present"

# ------------------------------- [10e] directory-listing harvesting -------
# an "Index of" page is not just a finding — its entries are files to grab
n_harv=0
banner "[10e] DIRECTORY-LISTING HARVEST"
mapfile -t LS_DIRS < <(awk -F'\t' '$3 ~ /\/$/ {print $3}' "$RESULTS" \
    | grep -vE "^[a-z]+://[^/]+/$" | sort -u | head -10)
info "listing harvest: ${#LS_DIRS[@]} director(y/ies) queued"
for ld in "${LS_DIRS[@]}"; do
    lbody="$(mktemp)"
    curl "${CURL_ARGS[@]}" -o "$lbody" "$ld" 2>/dev/null
    grep -qi "index of" "$lbody" || { rm -f "$lbody"; continue; }
    while read -r entry; do
        [ -z "$entry" ] && continue
        case "$entry" in
            /|..|*/|\?*) continue ;;
        esac
        furl="${ld}${entry}"
        read -r fsc fsz < <(curl "${CURL_ARGS[@]}" -o /dev/null \
            -w '%{http_code} %{size_download}' "$furl")
        [ "$fsc" = 200 ] || continue
        printf '%s\t%s\t%s\t(listing)\n' "$fsc" "$fsz" "$furl" >> "$RESULTS"
        case "$entry" in
            *.sql|*.bak|*.zip|*.tgz|*.log|*.env|*.old|*.save|*dump*|*pass*)
                warn "LISTING FILE (sensitive): $furl -> 200 (${fsz}B)" ;;
            *) info "listing file: $furl (${fsz}B)" ;;
        esac
        n_harv=$((n_harv+1))
    done < <(grep -ioP '(?<=href=")[^"]+' "$lbody" \
        | grep -vE '^(\.|/|\?|http)' | sort -u | head -20)
    rm -f "$lbody"
done
[ "$n_harv" -gt 0 ] && good "listing harvest: $n_harv file(s) recovered"

# -------------------------------------------- [10d] form inventory ---------
banner "[10d] FORM INVENTORY - injection / brute-force targets"
FPAGES="$(mktemp)"
cp "$OUT/root.html" "$FPAGES" 2>/dev/null
{
    awk -F'\t' '$1==200 && $3 ~ /\.(html?|aspx|php)(\/)?(\t|$)/ {print $3}' \
        "$RESULTS" | sort -u | head -4
    awk -F'\t' '$1==200 && $3 ~ /(login|signin|register|signup)(\/|\t|$)/ \
        {print $3}' "$RESULTS" | sort -u | head -2
} | sort -u | while read -r fp; do
    curl "${CURL_ARGS[@]}" -s -m 10 "$fp" >> "$FPAGES" 2>/dev/null
    echo >> "$FPAGES"
done
python3 - "$FPAGES" > "$OUT/forms.txt" <<'PYFORMS'
import re, sys
try:
    html = open(sys.argv[1], errors="replace").read()
except Exception:
    sys.exit(0)
for m in re.finditer(r'<form[^>]*>(.*?)</form>', html, re.S | re.I):
    tag = m.group(0)[:m.group(0).find(">")]
    action = re.search(r'action=["\']?([^"\' >]+)', tag, re.I)
    method = re.search(r'method=["\']?([^"\' >]+)', tag, re.I)
    inputs = re.findall(
        r'<input[^>]*name=["\']?([^"\' >]+)[^>]*>', m.group(1), re.I)
    print(f"action={action.group(1) if action else '(self)'} "
          f"method={method.group(1) if method else 'GET'} "
          f"inputs={','.join(inputs) if inputs else '-'}")
PYFORMS
rm -f "$FPAGES"
if [ -s "$OUT/forms.txt" ]; then
    good "$(wc -l < "$OUT/forms.txt") form(s) inventoried (forms.txt):"
    sed 's/^/    /' "$OUT/forms.txt" | head -6
    grep -q "password" "$OUT/forms.txt" \
        && warn "password input found - credential attack target (see attack-plan.txt)"
else
    info "no HTML forms found"
fi

# --------------------------------------------------- [11] opt-in tools ----
if [ "$RUN_NIKTO" = 1 ] && have nikto; then
    banner "[10a] NIKTO"
    nikto -h "$BASE" $( [ -n "$VH" ] && printf ' -vhost %s' "$VH" ) \
        "${HDR_NIKTO[@]}" \
        -Format txt -output "$OUT/nikto.txt" 2>&1 | tail -5
fi
if [ "$RUN_NUCLEI" = 1 ]; then
    if ! [ -d "$HOME/nuclei-templates" ]; then
        warn "nuclei templates not found - run once: nuclei -update-templates"
    fi
    if have nuclei; then
        banner "[11c] NUCLEI templates"
        HDR_NUCLEI=()
        for h in "${TOOL_HDRS[@]:-}"; do
            [ -n "$h" ] && HDR_NUCLEI+=(-H "$h")
        done
        nuclei -u "${BASE%*/}" -silent -nc "${HDR_NUCLEI[@]}" \
            -o "$OUT/nuclei.txt" 2>&1 | tail -5 || true
        [ -s "$OUT/nuclei.txt" ] \
            && { good "nuclei findings:"; sed 's/^/    /' "$OUT/nuclei.txt" | head -20; } \
            || info "nuclei: no findings"
    else
        warn "nuclei not installed - apt install nuclei (or go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest)"
    fi
fi
if [ "$RUN_NMAP" = 1 ] && have nmap; then
    banner "[10b] NMAP service scan"
    info "full TCP port sweep with service detection (this takes a few minutes)"
    nmap -sV -Pn --open -p- --min-rate 2000 --version-light \
        "$HOST" -oN "$OUT/nmap.txt" 2>&1 | tail -25
fi

# ------------------------------------------------------------ [11] report -
banner "[✓] SUMMARY"

# credential attack plan: hydrate brute-force commands with the usernames,
# login URL and field names actually discovered during this scan
# (subshell: the early "exit" only ends plan generation, not the scan)
(
    login_url="$(grep -E '/(login|signin|sign-in|wp-login)' "$RESULTS" \
        | awk -F'\t' '{print $3}' | head -1)"
    if [ -z "$login_url" ]; then
        echo "# no login endpoint discovered - no credential plan"
        exit 0
    fi
    echo "# Credential attack plan (discovered $(date '+%F %T'))"
    echo "login_url=$login_url"
    grep -q "password" "$OUT/forms.txt" 2>/dev/null \
        && grep "password" "$OUT/forms.txt" | head -2
    if [ -s "$OUT/name-candidates.txt" ]; then
        cp "$OUT/name-candidates.txt" "$OUT/brute-users.txt"
        echo "users_file=$OUT/brute-users.txt ($(wc -l < "$OUT/brute-users.txt") names)"
    fi
    path="$(printf '%s' "$login_url" | sed -E 's#^[a-z]+://[^/]+##')"
    echo
    echo "# hydra (POST form):"
    echo "hydra -L brute-users.txt -P /usr/share/wordlists/rockyou.txt \
        ${HOST} http-post-form \"${path}:username=^USER^&password=^PASS^:F=incorrect\""
    echo "# ffuf (JSON login):"
    echo "ffuf -w brute-users.txt:/usr/share/wordlists/rockyou.txt -X POST \
        -H 'Content-Type: application/x-www-form-urlencoded' \
        -d 'username=FUZZ&password=FUZZ' -u $login_url -mc 200,302"
) > "$OUT/attack-plan.txt"
{
    echo "# Web Recon Report — $BASEDISPLAY"
    echo
    echo "*run: $(date '+%Y-%m-%d %H:%M') — engine $ENGINE, wordlist $(basename "$WL")*"
    echo
    echo "## Contents of this directory"
    echo
    echo "| file | phase |"
    echo "|---|---|"
    echo "| whatweb.txt | fingerprint |"
    echo "| root-headers.txt / root.html | root response |"
    [ "$SCHEME" = https ] && echo "| tls.txt | certificate |"
    echo "| ferox.txt / ffuf.json / gobuster.txt | raw content discovery |"
    echo "| results.txt | normalized findings (STATUS, SIZE, URL) |"
    [ -s "$OUT/vhosts-found.txt" ] && echo "| vhosts-found.txt | vhost fuzzing |"
    [ -f "$OUT/ua-diff.txt" ] && echo "| ua-diff.txt | UA differentials |"
    [ -f "$OUT/bypass.txt" ] && echo "| bypass.txt | 403/401 bypasses |"
    [ -f "$OUT/comments.txt" ] && echo "| comments.txt | HTML comments |"
    [ -f "$OUT/js-secrets.txt" ] && echo "| js-secrets.txt | JS secrets |"
    [ -s "$OUT/api-endpoints.txt" ] && echo "| api-endpoints.txt | endpoints from API specs |"
    [ -s "$OUT/methods-matrix.txt" ] && echo "| methods-matrix.txt | Allow header per endpoint |"
    [ -s "$OUT/risky-methods.txt" ] && echo "| risky-methods.txt | endpoints allowing risky verbs |"
    [ -f "$OUT/nikto.txt" ] && echo "| nikto.txt | nikto |"
    [ -f "$OUT/nmap.txt" ] && echo "| nmap.txt | nmap |"
    echo
    echo "## Findings by severity"
    echo
    HIGH="(bypass.txt)|((risky-methods.txt))|(js-secrets.txt)|(auth-creds.txt)"
    echo "### High (exploit-ready)"
    echo
    for f in bypass.txt js-secrets.txt risky-methods.txt auth-creds.txt params-found.txt; do
        if [ -s "$OUT/$f" ]; then
            echo "- **$f**:"
            echo '```'
            head -8 "$OUT/$f"
            [ "$(wc -l < "$OUT/$f")" -gt 8 ] && echo "... ($(wc -l < "$OUT/$f") total)"
            echo '```'
        fi
    done
    grep -qE '\.git|\.env|backup\.(zip|tgz|tar)|dump\.sql' "$RESULTS" && \
        { echo "- **source/backup disclosure**:"; echo '```'; \
          grep -E '\.git|\.env|backup\.(zip|tgz|tar)|dump\.sql' "$RESULTS" | head -6; echo '```'; }
    echo
    echo "### Medium (recon advantage)"
    echo
    for f in vhosts-found.txt ua-diff.txt api-endpoints.txt methods-matrix.txt auth-new-paths.txt params-found.txt; do
        [ -s "$OUT/$f" ] && { echo "- $f ($(wc -l < "$OUT/$f") entries)"; }
    done
    grep -aq "SOURCE MAP" "$OUT/console.log" 2>/dev/null && \
        echo "- source maps exposed (original source recoverable)"
    [ -s "$OUT/methods-matrix.txt" ] && \
        echo "- $(wc -l < "$OUT/methods-matrix.txt") endpoints expose Allow headers"
    echo
    echo "### Info"
    echo
    echo "- $TOTAL discovered paths (results.txt)"
    [ -n "$VH" ] && echo "- vhost routing: $VH"
    echo

    echo "## Discovered paths"
    echo
    echo '```'
    sort -t$'\t' -k1,1n "$RESULTS" | column -t -s$'\t'
    echo '```'
    echo
    echo "## Next steps"
    echo
    grep -q '401\|403' "$RESULTS" && \
        echo "- 401/403 paths present — see bypass.txt; try feroxbuster on them with adjusted headers"
    grep -q '\.git' "$RESULTS" && \
        echo "- .git exposed — git-dumper $BASE.git"
    grep -qiE 'wordpress|wp-' "$OUT/whatweb.txt" 2>/dev/null && \
        echo "- WordPress — wpscan --url $BASEDISPLAY"
    [ -s "$OUT/vhosts-found.txt" ] && \
        echo "- vhosts found — add to /etc/hosts, re-run this script against each"
    [ -s "$OUT/api-endpoints.txt" ] && \
        echo "- API spec found — test every endpoint in api-endpoints.txt for auth bypass and IDOR"
    [ -s "$OUT/risky-methods.txt" ] && \
        echo "- risky methods allowed (see risky-methods.txt) — PUT: try uploading a webshell; WebDAV verbs: run davtest"
    [ -s "$OUT/attack-plan.txt" ] && \
        echo "- credential attack plan ready: attack-plan.txt (hydra/ffuf commands hydrated with discovered users)"
    [ -s "$OUT/idor-found.txt" ] && \
        echo "- IDOR candidates: $(wc -l < "$OUT/idor-found.txt") accessible object(s) — test enumeration with other IDs"
    [ -s "$OUT/default-creds-hit.txt" ] && \
        echo "- DEFAULT CREDENTIALS WORK: see default-creds-hit.txt"
    grep -qiE 'login|signin' "$RESULTS" && \
        echo "- login page present - credential attacks: hydra -L $OUT/name-candidates.txt -P /usr/share/wordlists/rockyou.txt <login-url> http-post-form"
    grep -oE '[A-Za-z][A-Za-z0-9_-]{2,}\[[0-9][0-9a-zA-Z.\-]*\]' \
        "$OUT/whatweb.txt" 2>/dev/null | head -4 | while read -r pv; do
            prod="$(printf '%s' "$pv" | sed -E 's/\[.*//')"
            ver="$(printf '%s' "$pv" | sed -E 's/.*\[//; s/\]//')"
            echo "- known version: $prod $ver - check: searchsploit $prod"
        done
    echo "- deeper fuzz: feroxbuster -u $BASEDISPLAY -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -d 2"
} > "$OUT/report.md"

good "$(wc -l < "$RESULTS") paths — full inventory in $OUT/results.txt"
good "report: $OUT/report.md"
echo
