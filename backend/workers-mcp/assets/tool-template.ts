// MCP Tool Template for Cloudflare Workers
// Copy this file to create new tools in src/workers/mcp/tools/

/**
 * Tool name template
 * @tool template_tool
 * @description A clear one-line description of what this tool does
 * @free | @pro (choose one)
 */
export async function templateTool(
  input: TemplateToolInput,
  env: Env,
  ctx: ExecutionContext
): Promise<TemplateToolOutput> {
  // ============================================================================
  // STEP 1: Validate input
  // ============================================================================
  if (!input.query?.trim()) {
    throw new Error('Query is required');
  }

  // ============================================================================
  // STEP 2: Authenticate and get user context
  // ============================================================================
  const userId = await getUserId(request);
  const tenantId = await getTenantId(userId, env);

  // ============================================================================
  // STEP 3: Check license (if Pro feature)
  // ============================================================================
  // Uncomment if Pro feature:
  // const license = await licenseVerifier.verify(env, userId);
  // if (!licenseVerifier.hasFeature(license, 'templateTool')) {
  //   throw new Error('templateTool requires Pro subscription');
  // }

  // ============================================================================
  // STEP 4: Check rate limits
  // ============================================================================
  const rateLimit = await rateLimiter.check(
    env.RATE_LIMITS,
    `templateTool:${userId}`,
    100, // 100 requests
    60000 // per minute
  );
  if (!rateLimit.allowed) {
    throw new Error(`Rate limit exceeded. Retry in ${rateLimit.retryAfter}s`);
  }

  // ============================================================================
  // STEP 5: Execute main logic
  // ============================================================================
  const results = await env.DB.prepare(`
    SELECT * FROM data
    WHERE tenant_id = ? AND query = ?
  `).bind(tenantId, input.query).all();

  // ============================================================================
  // STEP 6: Return structured output
  // ============================================================================
  return {
    results: results.results,
    total: results.results.length,
  };
}

// ============================================================================
// TYPES
// ============================================================================
export interface TemplateToolInput {
  query: string;
  limit?: number;
}

export interface TemplateToolOutput {
  results: Array<{
    id: string;
    data: any;
  }>;
  total: number;
}

// ============================================================================
// HELPERS
// ============================================================================
async function getUserId(request: Request): Promise<string> {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader?.replace('Bearer ', '');
  if (!token) throw new Error('Authentication required');
  const payload = await verifyJWT(token, env.JWT_SECRET);
  return payload.userId;
}

async function getTenantId(userId: string, env: Env): Promise<string> {
  const result = await env.DB.prepare(
    'SELECT tenant_id FROM users WHERE id = ?'
  ).bind(userId).first();
  if (!result) throw new Error('User not found');
  return result.tenant_id;
}
