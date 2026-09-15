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
EXTENSIONS="php,html,bak,old,txt,zip,sql,json"
COOKIES=""
PROXY=""
RUN_NIKTO=0 RUN_NMAP=0
DO_VHOST=1 DO_UA=1 DO_BYPASS=1 DO_JS=1 DO_CONTENT=1
EXTRA_HDRS=()

usage() {
    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
    cat <<'FLAGS'

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
[ -n "$TARGET" ] || usage
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
    SCHEME="$lscheme"; PORT="$lport"; BASE="$_nbase"; code="$rc"
    if [ "$lhost" != "$HOST" ]; then
        # adopt the vhost name only if the same request WITHOUT the Host
        # override still redirects — proof of name-based routing
        rc_ip="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "$_nbase")"
        case "$rc_ip" in 301|302|307|308)
            VH="$lhost"
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
        "${BASE%*/}" > "$OUT/whatweb.txt" 2>&1 || true
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
if [ "$DO_CONTENT" = 1 ]; then
    banner "[5] CONTENT DISCOVERY — $ENGINE (depth $DEPTH, extensions)"
    FEROX_STATUS="200,204,301,302,307,308,401,403,405,500"
    case "$ENGINE" in
        feroxbuster)
            feroxbuster -u "$BASE" -w "$WL" -x "$EXTENSIONS" -d "$DEPTH" \
                -t "$THREADS" -k --auto-tune --extract-links \
                -s "$FEROX_STATUS" "${HDR_FEROX[@]}" "${PROXY_FEROX[@]}" \
                -o "$OUT/ferox.txt" --no-state 2>&1 | tail -20
            ;;
        ffuf)
            ffuf -u "${BASE%*/}/FUZZ" -w "$WL" -recursion -recursion-depth "$DEPTH" \
                -e "$EXTENSIONS" -ac -t "$THREADS" -k \
                "${HDR_FFUF[@]}" "${PROXY_FFUF[@]}" \
                -of json -o "$OUT/ffuf.json" 2>&1 | tail -5
            ;;
        gobuster)
            gobuster dir -u "$BASE" -w "$WL" -x "$EXTENSIONS" -t "$THREADS" -k \
                -s "200,204,301,302,307,308,401,403,405,500" --no-error \
                "${HDR_GOB[@]}" "${PROXY_GOB[@]}" \
                -o "$OUT/gobuster.txt" 2>&1 | tail -5
            ;;
    esac
fi

# normalize engine output -> results.txt (STATUS<TAB>SIZE<TAB>URL)
RESULTS="$OUT/results.txt"; : > "$RESULTS"
if [ -f "$OUT/ferox.txt" ]; then
    grep -E '^[0-9]{3}' "$OUT/ferox.txt" | awk '{
        s = $5; sub(/c$/, "", s);
        loc = ($7 == "=>") ? "\t-> " $8 : "";
        print $1 "\t" s "\t" $6 loc
    }' >> "$RESULTS"
elif [ -f "$OUT/ffuf.json" ]; then
    python3 - "$OUT/ffuf.json" >> "$RESULTS" <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    for r in d.get("results", []):
        print(f'{r["status"]}\t{r["length"]}\t{r["url"]}')
except Exception as e:
    sys.stderr.write(str(e))
PYEOF
elif [ -f "$OUT/gobuster.txt" ]; then
    grep -oP 'Found: \K.*\(Status: \d+\).*' "$OUT/gobuster.txt" 2>/dev/null \
        | sed -E 's/(.*) \(Status: ([0-9]+)\) \[Size: ([0-9]+)\]/\2\t\3\t\1/' >> "$RESULTS"
fi
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
        _tp="/${turl#*://}"; _tp="/${_tp#*/}"
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
    if [ -n "$VHOSTLIST" ]; then cp "$VHOSTLIST" "$NAMES"; else
        printf '%s\n' admin api app auth backup beta blog cdn cms console \
            dashboard data db demo dev docs download files forum git help \
            home intranet jenkins lab legacy mail media monitor mx news old \
            panel portal private prod public remote restricted s3 shop site \
            staff staging static store support test testing vpn web wiki \
            www internal localhost > "$NAMES"
    fi
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
        grep -oE '"(/[a-zA-Z0-9_./-]{3,40})"' /tmp/js-$$.js \
            | tr -d '"' | sort -u | head -20 | while read -r p; do
            case "$p" in *.css|*.png|*.jpg|*.svg|*.woff*|*.map) continue ;; esac
            sc="$(curl "${CURL_ARGS[@]}" -o /dev/null -w '%{http_code}' "${BASE%*/}$p")"
            case "$sc" in 200|301|302|401|403)
                good "JS endpoint $p -> $sc"
                printf '%s\t%s\t%s\n' "$sc" "js" "${BASE%*/}$p" >> "$RESULTS" ;;
            esac
        done
        rm -f /tmp/js-$$.js
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

# --------------------------------------------------- [10] opt-in tools ----
if [ "$RUN_NIKTO" = 1 ] && have nikto; then
    banner "[10a] NIKTO"
    nikto -h "$BASE" $( [ -n "$VH" ] && printf ' -vhost %s' "$VH" ) \
        "${HDR_NIKTO[@]}" \
        -Format txt -output "$OUT/nikto.txt" 2>&1 | tail -5
fi
if [ "$RUN_NMAP" = 1 ] && have nmap; then
    banner "[10b] NMAP service scan"
    info "full TCP port sweep with service detection (this takes a few minutes)"
    nmap -sV -Pn --open -p- --min-rate 2000 --version-light \
        "$HOST" -oN "$OUT/nmap.txt" 2>&1 | tail -25
fi

# ------------------------------------------------------------ [11] report -
banner "[✓] SUMMARY"
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
    [ -f "$OUT/nikto.txt" ] && echo "| nikto.txt | nikto |"
    [ -f "$OUT/nmap.txt" ] && echo "| nmap.txt | nmap |"
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
    echo "- deeper fuzz: feroxbuster -u $BASEDISPLAY -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -d 2"
} > "$OUT/report.md"

good "$(wc -l < "$RESULTS") paths — full inventory in $OUT/results.txt"
good "report: $OUT/report.md"
echo
