import { z } from "zod";

/**
 * Standard API error envelope that supports good UX.
 * Use `fieldErrors` for inline form errors; otherwise rely on `message`.
 */
export const ApiErrorSchema = z.object({
  ok: z.literal(false),
  code: z.string(), // e.g. "AUTH_EXPIRED", "VALIDATION_ERROR", "NOT_FOUND"
  message: z.string(),
  requestId: z.string().optional(),
  fieldErrors: z.record(z.array(z.string())).optional()
});

export type ApiError = z.infer<typeof ApiErrorSchema>;

/**
 * Example success envelope:
 */
export const ApiOkSchema = z.object({
  ok: z.literal(true),
  data: z.unknown()
});
