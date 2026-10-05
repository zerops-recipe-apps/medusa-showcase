import type { IApiKeyModuleService } from "@medusajs/framework/types"
import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"
import { Modules } from "@medusajs/framework/utils"

/**
 * Lets nextstore load the publishable key from Medusa when project vault
 * CHANNEL_PUBLISHABLE_KEY is not on the storefront container yet.
 * Protected by RELOAD_SECRET (same as nextstore reload-env).
 */
export async function GET(
  req: MedusaRequest,
  res: MedusaResponse
): Promise<void> {
  const secret = process.env.RELOAD_SECRET
  const provided = req.headers["x-reload-secret"]

  if (!secret || typeof provided !== "string" || provided !== secret) {
    res.status(403).json({ message: "Forbidden" })
    return
  }

  const service = req.scope.resolve<IApiKeyModuleService>(Modules.API_KEY)
  const apiKeys = await service.listApiKeys()
  const publishableKey =
    apiKeys.find((key) => key.type === "publishable") ?? apiKeys.at(0)

  if (!publishableKey?.token) {
    res.status(404).json({ message: "No publishable API key found" })
    return
  }

  res.json({ token: publishableKey.token })
}
