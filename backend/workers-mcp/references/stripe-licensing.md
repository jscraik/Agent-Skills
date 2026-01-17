# Stripe Subscription Licensing

Implement feature-based licensing with Stripe subscriptions for Cloudflare Workers MCP servers.

## Architecture Overview

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   User      │──Upgrade▶│   Stripe    │──Webhook▶│   Worker     │
│   Request   │         │   Checkout  │         │   Server     │
└─────────────┘         └─────────────┘         └──────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                        ┌─────────────┐         ┌──────────────┐
                        │   Stripe    │         │   D1 / KV    │
                        │   Portal    │         │   Storage    │
                        └─────────────┘         └──────────────┘
```

## Stripe Setup

### 1. Create Stripe Products and Prices

In Stripe Dashboard:
1. **Products** → **Add product**
   - **Name**: `Pro Plan`
   - **Description**: `Advanced features for power users`
   - **Pricing**: `$9/month`

2. Copy the **Price ID** (starts with `price_`)

### 2. Configure Webhook

1. **Developers** → **Webhooks** → **Add endpoint**
2. **Endpoint URL**: `https://your-worker.workers.dev/webhooks/stripe`
3. **Events to listen to**:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

3. Copy the **Webhook Secret** (starts with `whsec_`)

## Environment Configuration

```toml
# wrangler.toml
[vars]
STRIPE_PRO_PRICE_ID = "price_xxxxx"
STRIPE_TEAM_PRICE_ID = "price_yyyyy"
```

Secrets:
```bash
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_WEBHOOK_SECRET
```

## License Verifier Implementation

```typescript
// src/lib/license/verifier.ts
export interface LicenseInfo {
  userId: string;
  tenantId: string;
  plan: 'free' | 'pro' | 'team';
  features: string[];
  limits: {
    memories: number;
    apiCallsPerMonth: number;
  };
  expiresAt?: Date;
}

export class LicenseVerifier {
  private cache = new Map<string, { license: LicenseInfo; expiresAt: number }>();

  async verify(env: Env, userId: string): Promise<LicenseInfo> {
    // Check KV cache first (5 min TTL)
    const cached = await env.CACHE.get(`license:${userId}`, 'json');
    if (cached) {
      return cached as LicenseInfo;
    }

    // Get from database
    const stmt = env.DB.prepare(`
      SELECT
        t.plan,
        u.id as user_id,
        u.tenant_id
      FROM users u
      JOIN tenants t ON u.tenant_id = t.id
      WHERE u.id = ?
    `);

    const result = await stmt.bind(userId).first();

    if (!result) {
      throw new Error('User not found');
    }

    const license: LicenseInfo = {
      userId,
      tenantId: result.tenant_id,
      plan: result.plan,
      features: this.getFeaturesForPlan(result.plan),
      limits: this.getLimitsForPlan(result.plan),
    };

    // Cache for 5 minutes
    await env.CACHE.put(
      `license:${userId}`,
      JSON.stringify(license),
      { expirationTtl: 300 }
    );

    return license;
  }

  hasFeature(license: LicenseInfo, feature: string): boolean {
    return license.features.includes(feature);
  }

  async checkLimit(
    env: Env,
    license: LicenseInfo,
    resource: 'memories' | 'apiCalls'
  ): Promise<boolean> {
    const limit = license.limits[resource];
    if (limit === -1) return true; // Unlimited

    // Check current usage
    const stmt = env.DB.prepare(`
      SELECT COUNT(*) as count FROM memories
      WHERE tenant_id = ? AND deleted_at IS NULL
    `);

    const { count } = await stmt.bind(license.tenantId).first();

    return count < limit;
  }

  private getFeaturesForPlan(plan: string): string[] {
    switch (plan) {
      case 'free':
        return ['remember', 'recall', 'list_memories', 'delete_memory'];
      case 'pro':
        return [
          'remember', 'recall', 'list_memories', 'delete_memory',
          'semantic_search', 'analyze_memories',
        ];
      case 'team':
        return [
          'remember', 'recall', 'list_memories', 'delete_memory',
          'semantic_search', 'analyze_memories', 'export_data',
        ];
      default:
        return [];
    }
  }

  private getLimitsForPlan(plan: string) {
    switch (plan) {
      case 'free':
        return { memories: 1000, apiCallsPerMonth: 10000 };
      case 'pro':
        return { memories: 50000, apiCallsPerMonth: 100000 };
      case 'team':
        return { memories: 200000, apiCallsPerMonth: 500000 };
      default:
        return { memories: 1000, apiCallsPerMonth: 10000 };
    }
  }
}
```

## Stripe Client Implementation

```typescript
// src/lib/license/stripe.ts
import Stripe from 'stripe';

export class StripeLicenseManager {
  private stripe: Stripe;

  constructor(secretKey: string) {
    this.stripe = new Stripe(secretKey);
  }

  /**
   * Create checkout session for upgrade
   */
  async createCheckoutSession(
    customerId: string,
    priceId: string,
    successUrl: string,
    cancelUrl: string,
    metadata?: Record<string, string>
  ): Promise<string> {
    const session = await this.stripe.checkout.sessions.create({
      customer: customerId,
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: successUrl,
      cancel_url: cancelUrl,
      metadata: metadata || {},
    });

    return session.url!;
  }

  /**
   * Create customer portal session
   */
  async createPortalSession(
    customerId: string,
    returnUrl: string
  ): Promise<string> {
    const session = await this.stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl,
    });

    return session.url;
  }

  /**
   * Handle Stripe webhooks
   */
  async handleWebhook(
    payload: string,
    signature: string,
    webhookSecret: string,
    env: Env
  ): Promise<void> {
    const event = this.stripe.webhooks.constructEvent(
      payload,
      signature,
      webhookSecret
    );

    switch (event.type) {
      case 'checkout.session.completed':
        await this.handleCheckoutCompleted(event.data.object, env);
        break;

      case 'customer.subscription.updated':
        await this.handleSubscriptionUpdated(event.data.object, env);
        break;

      case 'customer.subscription.deleted':
        await this.handleSubscriptionDeleted(event.data.object, env);
        break;

      case 'invoice.payment_succeeded':
        await this.handleInvoicePaymentSucceeded(event.data.object, env);
        break;

      case 'invoice.payment_failed':
        await this.handleInvoicePaymentFailed(event.data.object, env);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
  }

  private async handleCheckoutCompleted(session: any, env: Env): Promise<void> {
    const tenantId = session.metadata?.tenant_id;
    const customerId = session.customer;

    if (!tenantId) {
      console.error('Missing tenant_id in session metadata');
      return;
    }

    // Update tenant plan based on price
    const plan = this.getPricePlan(session.subscription.items.data[0].price.id);

    await env.DB.prepare(`
      UPDATE tenants
      SET plan = ?, updated_at = ?
      WHERE id = ?
    `).bind(plan, Date.now(), tenantId).run();

    // Create subscription record
    await env.DB.prepare(`
      INSERT INTO subscriptions (
        id, tenant_id, stripe_subscription_id, stripe_customer_id,
        plan, status, current_period_start, current_period_end,
        created_at, updated_at
      )
      VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
    `).bind(
      crypto.randomUUID(),
      tenantId,
      session.subscription,
      customerId,
      plan,
      session.subscription.current_period_start,
      session.subscription.current_period_end,
      Date.now(),
      Date.now()
    ).run();

    // Invalidate license cache
    await this.invalidateTenantLicenseCache(env, tenantId);
  }

  private async handleSubscriptionUpdated(subscription: any, env: Env): Promise<void> {
    const stripeSubId = subscription.id;

    // Get subscription record
    const subRecord = await env.DB.prepare(`
      SELECT tenant_id FROM subscriptions WHERE stripe_subscription_id = ?
    `).bind(stripeSubId).first();

    if (!subRecord) return;

    // Update status
    await env.DB.prepare(`
      UPDATE subscriptions
      SET status = ?,
          current_period_start = ?,
          current_period_end = ?,
          updated_at = ?
      WHERE stripe_subscription_id = ?
    `).bind(
      subscription.status,
      subscription.current_period_start,
      subscription.current_period_end,
      Date.now(),
      stripeSubId
    ).run();

    // Invalidate license cache
    await this.invalidateTenantLicenseCache(env, subRecord.tenant_id);
  }

  private async handleSubscriptionDeleted(subscription: any, env: Env): Promise<void> {
    const stripeSubId = subscription.id;

    // Downgrade to free
    await env.DB.prepare(`
      UPDATE tenants
      SET plan = 'free', updated_at = ?
      WHERE id = (
        SELECT tenant_id FROM subscriptions WHERE stripe_subscription_id = ?
      )
    `).bind(Date.now(), stripeSubId).run();

    // Invalidate license cache
    await this.invalidateTenantLicenseCache(env, subscription.metadata?.tenant_id);
  }

  private async handleInvoicePaymentSucceeded(invoice: any, env: Env): Promise<void> {
    // Track successful payment for analytics
    // Could record usage for metered billing
  }

  private async handleInvoicePaymentFailed(invoice: any, env: Env): Promise<void> {
    // Notify user of payment failure
    // Could send email or create notification
  }

  private getPricePlan(priceId: string): string {
    // Map price IDs to plans
    if (priceId === this.env.STRIPE_PRO_PRICE_ID) return 'pro';
    if (priceId === this.env.STRIPE_TEAM_PRICE_ID) return 'team';
    return 'free';
  }

  private async invalidateTenantLicenseCache(env: Env, tenantId: string): Promise<void> {
    // Get all users for tenant
    const users = await env.DB.prepare(`
      SELECT id FROM users WHERE tenant_id = ?
    `).bind(tenantId).all();

    // Invalidate cache for each user
    for (const user of users.results) {
      await env.CACHE.delete(`license:${user.id}`);
    }
  }
}
```

## Usage in MCP Tools

```typescript
// In your Worker class
private license = new LicenseVerifier();

async semanticSearch(query: string, limit: number = 10) {
  const userId = await this.getUserId();

  // Check license
  const license = await this.license.verify(this.env, userId);

  if (!this.license.hasFeature(license, 'semantic_search')) {
    throw new Error(
      'semantic_search requires Pro subscription. ' +
      'Upgrade at https://app.yourdomain.com/upgrade'
    );
  }

  // Check limits
  const withinLimit = await this.license.checkLimit(this.env, license, 'apiCalls');
  if (!withinLimit) {
    throw new Error(
      'API limit exceeded. Upgrade for higher limits.'
    );
  }

  // Execute feature
  return await this.performSemanticSearch(query, limit);
}
```

## Webhook Handler

```typescript
// In Worker fetch method
async fetch(request: Request): Promise<Response> {
  const url = new URL(request.url);

  if (url.pathname === '/webhooks/stripe') {
    return this.handleStripeWebhook(request);
  }

  return new ProxyToSelf(this).fetch(request);
}

private async handleStripeWebhook(request: Request): Promise<Response> {
  const signature = request.headers.get('Stripe-Signature');
  const payload = await request.text();

  const stripeManager = new StripeLicenseManager(this.env.STRIPE_SECRET_KEY);

  try {
    await stripeManager.handleWebhook(
      payload,
      signature,
      this.env.STRIPE_WEBHOOK_SECRET,
      this.env
    );
    return new Response('OK', { status: 200 });
  } catch (error) {
    console.error('Webhook error:', error);
    return new Response('Webhook error', { status: 400 });
  }
}
```

## Upgrade Flow

1. User triggers upgrade in your app
2. Call `stripeManager.createCheckoutSession()` with:
   - `customerId`: User's Stripe customer ID
   - `priceId`: `STRIPE_PRO_PRICE_ID`
   - `successUrl`: Redirect after successful payment
   - `cancelUrl`: Redirect if cancelled
   - `metadata`: `{ tenant_id: '...' }`
3. Redirect user to checkout URL
4. After payment, Stripe sends webhook to `/webhooks/stripe`
5. Webhook handler updates tenant plan in D1
6. License cache is invalidated
7. Next API call gets new license with Pro features

## Best Practices

1. **Cache Invalidation**: Always invalidate license cache after plan changes
2. **Graceful Degradation**: Allow read access to old data after downgrade
3. **Prorated Billing**: Use Stripe's proration settings for mid-cycle upgrades
4. **Payment Failure Handling**: Grace period before feature revocation
5. **Usage Tracking**: Track API calls per month for accurate limits
6. **Testing**: Use Stripe test mode and test webhooks

## Troubleshooting

### Common Issues

1. **Webhook not received**: Check Stripe webhook endpoint is reachable
2. **Plan not updated**: Verify webhook signature is correct
3. **License cache stale**: Ensure cache invalidation runs
4. **Price ID mismatch**: Verify price IDs match between environments

### Debug Logging

```typescript
console.log(JSON.stringify({
  type: 'stripe_webhook',
  event: event.type,
  tenant_id: tenantId,
  plan: plan,
  timestamp: Date.now(),
}));
```
