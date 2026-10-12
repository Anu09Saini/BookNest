#!/usr/bin/env bash
# BookNest API curl helper. Run from the project root.
set -euo pipefail
BASE_URL="${BOOKNEST_BASE_URL:-http://127.0.0.1:8000}"
COOKIE_JAR="${BOOKNEST_COOKIE_JAR:-/tmp/booknest-cookies.txt}"
MEMBER_TOKEN="${BOOKNEST_MEMBER_TOKEN:-}"
API_KEY="${BOOKNEST_PARTNER_API_KEY:-}"
API_SECRET="${BOOKNEST_PARTNER_API_SECRET:-}"

usage() {
  cat <<'EOF'
Usage:
  scripts/booknest_curl.sh health
  scripts/booknest_curl.sh books
  scripts/booknest_curl.sh book BOOK_ID
  scripts/booknest_curl.sh member-login EMAIL PASSWORD
  scripts/booknest_curl.sh member-me | member-loans | member-fines
  scripts/booknest_curl.sh staff-login EMAIL PASSWORD
  scripts/booknest_curl.sh staff-me | staff-logout
  scripts/booknest_curl.sh checkout MEMBER_ID COPY_ID YYYY-MM-DD
  scripts/booknest_curl.sh return LOAN_ID
  scripts/booknest_curl.sh pay-fine FINE_ID AMOUNT
  scripts/booknest_curl.sh overdue
  scripts/booknest_curl.sh popular [LIMIT]
  scripts/booknest_curl.sh partner-books

Environment:
  BOOKNEST_BASE_URL, BOOKNEST_COOKIE_JAR, BOOKNEST_MEMBER_TOKEN,
  BOOKNEST_PARTNER_API_KEY, BOOKNEST_PARTNER_API_SECRET
EOF
}
need_token() {
  [[ -n "$MEMBER_TOKEN" ]] || { echo "Set BOOKNEST_MEMBER_TOKEN to your JWT." >&2; exit 2; }
}
case "${1:-help}" in
  health) curl -i "$BASE_URL/health" ;;
  books) curl -i "$BASE_URL/books/" ;;
  book) [[ $# -eq 2 ]] || { usage; exit 2; }; curl -i "$BASE_URL/books/$2" ;;
  member-login)
    [[ $# -eq 3 ]] || { usage; exit 2; }
    curl -i -X POST "$BASE_URL/auth/member/login" -H "Content-Type: application/json" \
      -d "{\"email\":\"$2\",\"password\":\"$3\"}"
    ;;
  member-me) need_token; curl -i "$BASE_URL/members/me" -H "Authorization: Bearer $MEMBER_TOKEN" ;;
  member-loans) need_token; curl -i "$BASE_URL/members/me/loans" -H "Authorization: Bearer $MEMBER_TOKEN" ;;
  member-fines) need_token; curl -i "$BASE_URL/members/me/fines" -H "Authorization: Bearer $MEMBER_TOKEN" ;;
  staff-login)
    [[ $# -eq 3 ]] || { usage; exit 2; }
    curl -i -c "$COOKIE_JAR" -X POST "$BASE_URL/auth/staff/login" -H "Content-Type: application/json" \
      -d "{\"email\":\"$2\",\"password\":\"$3\"}"
    echo "Cookie jar saved to $COOKIE_JAR"
    ;;
  staff-me) curl -i -b "$COOKIE_JAR" "$BASE_URL/staff/me" ;;
  staff-logout) curl -i -b "$COOKIE_JAR" -c "$COOKIE_JAR" -X POST "$BASE_URL/auth/staff/logout" ;;
  checkout)
    [[ $# -eq 4 ]] || { usage; exit 2; }
    curl -i -b "$COOKIE_JAR" -X POST "$BASE_URL/loans" -H "Content-Type: application/json" \
      -d "{\"member_id\":$2,\"copy_id\":$3,\"due_date\":\"$4\"}"
    ;;
  return) [[ $# -eq 2 ]] || { usage; exit 2; }; curl -i -b "$COOKIE_JAR" -X POST "$BASE_URL/loans/$2/return" ;;
  pay-fine)
    [[ $# -eq 3 ]] || { usage; exit 2; }; need_token
    curl -i -X POST "$BASE_URL/fines/$2/payments" -H "Authorization: Bearer $MEMBER_TOKEN" \
      -H "Content-Type: application/json" -d "{\"amount\":$3}"
    ;;
  overdue) curl -i -b "$COOKIE_JAR" "$BASE_URL/reports/overdue-loans" ;;
  popular) limit="${2:-5}"; curl -i -b "$COOKIE_JAR" "$BASE_URL/reports/most-borrowed-books?limit=$limit" ;;
  partner-books)
    [[ -n "$API_KEY" && -n "$API_SECRET" ]] || { echo "Set partner credential environment variables." >&2; exit 2; }
    curl -i "$BASE_URL/partner/catalogue/books" -H "X-API-Key: $API_KEY" -H "X-API-Secret: $API_SECRET"
    ;;
  help|-h|--help) usage ;;
  *) echo "Unknown command: $1" >&2; usage; exit 2 ;;
esac
