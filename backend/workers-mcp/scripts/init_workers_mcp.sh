#!/bin/bash
# init_workers_mcp.sh - Scaffold a new Cloudflare Workers MCP server
# Usage: ./scripts/init_workers_mcp.sh <project-name> <destination>

set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  init_workers_mcp.sh [project-name] [destination]

Examples:
  init_workers_mcp.sh my-mcp-server .
  init_workers_mcp.sh
TXT
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

for arg in "$@"; do
  if [[ "$arg" == --* || "$arg" == -?* ]]; then
    echo "ERROR: unknown option: $arg"
    usage
    exit 2
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$SKILL_DIR/assets"

PROJECT_NAME=${1:-"my-mcp-server"}
DEST_DIR=${2:-"."}

echo "🏗️  Creating Workers MCP server: $PROJECT_NAME"

# Create project structure
mkdir -p "$DEST_DIR/$PROJECT_NAME"/{src/{workers/mcp/tools,durable-objects,lib/{db,kv,auth,license,embeddings,monitoring,types},middleware},migrations,scripts,tests/{unit,integration,contract}}

# Copy templates from assets
cp "$ASSETS_DIR/wrangler.template.toml" "$DEST_DIR/$PROJECT_NAME/wrangler.toml"
cp "$ASSETS_DIR/tool-template.ts" "$DEST_DIR/$PROJECT_NAME/src/workers/mcp/tools/template.ts"
cp "$ASSETS_DIR/d1-schema-template.sql" "$DEST_DIR/$PROJECT_NAME/migrations/001_initial.sql"

# Create package.json
cat > "$DEST_DIR/$PROJECT_NAME/package.json" << 'EOF'
{
  "name": "PROJECT_NAME",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "test": "vitest",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "workers-mcp": "^1.0.0"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20241218.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0",
    "wrangler": "^3.0.0"
  }
}
EOF

# Create tsconfig.json
cat > "$DEST_DIR/$PROJECT_NAME/tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022"],
    "types": ["@cloudflare/workers-types"],
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF

echo "✅ Workers MCP server scaffolded at: $DEST_DIR/$PROJECT_NAME"
echo ""
echo "Next steps:"
echo "  1. cd $DEST_DIR/$PROJECT_NAME"
echo "  2. npm install"
echo "  3. Edit wrangler.toml with your Cloudflare account details"
echo "  4. Create D1 database: wrangler d1 create DB"
echo "  5. Create KV namespaces: wrangler kv:namespace create CACHE"
