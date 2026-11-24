#!/bin/sh
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
# Regenerate the Markdown chat logs of the cloud session (main conversation + one per background agent).
# usage: export_all.sh <session transcript dir parent> <session id>
set -e
P=${1:-/root/.claude/projects/-home-user}; S=${2:-468ace82-a4b3-592d-8838-6ea52a1be021}
D=$(cd "$(dirname "$0")/.." && pwd); T="$D/tools/jsonl_to_md.py"
mkdir -p "$D/agents"
python3 "$T" "$P/$S.jsonl" "$D/session_2026-11-23_main.md" "Cloud session 2026-11-23/24: main conversation"
idx="$D/README.md"
{
echo "# Chat logs of the cloud session of 2026-11-23 / 24"
echo
echo "Generated from the session transcripts by \`tools/export_all.sh\` (converter \`tools/jsonl_to_md.py\`): user messages, assistant"
echo "replies, every tool call with its inputs, shortened tool results. Left out: the model's internal reasoning, injected system"
echo "reminders, private e-mail addresses. Times are UTC (CET = UTC+1). Regenerated at each push, so the newest part grows."
echo
echo "| log | what |"
echo "|---|---|"
echo "| [session_2026-11-23_main.md](session_2026-11-23_main.md) | the main conversation (user, coordinator) |"
for m in "$P/$S"/subagents/agent-*.meta.json; do
  id=$(basename "$m" .meta.json); j="$P/$S/subagents/$id.jsonl"; [ -f "$j" ] || continue
  desc=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('description','agent'))" "$m")
  stopped=$(python3 -c "import json,sys;print('stopped by the user' if json.load(open(sys.argv[1])).get('stoppedByUser') else '')" "$m")
  start=$(python3 -c "import json,sys
for l in open(sys.argv[1]):
  d=json.loads(l)
  if d.get('timestamp'): print(d['timestamp'][:16].replace('T',' ')); break" "$j")
  slug=$(echo "$desc" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9\n' '_' | sed 's/__*/_/g; s/_$//')
  out="agents/$(echo $start | cut -c1-10)_${slug}.md"
  python3 "$T" "$j" "$D/$out" "Background agent: $desc (started $start UTC)"
  echo "| [$out]($out) | background agent \"$desc\", started $start UTC ${stopped:+($stopped)} |"
done
} > "$idx"
