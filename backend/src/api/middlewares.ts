import {
  defineMiddlewares,
  type MedusaNextFunction,
  type MedusaRequest,
  type MedusaResponse,
} from "@medusajs/framework/http"

/**
 * Medusa sets secure session cookies in production. Behind Zerops (and other
 * reverse proxies) the app must see HTTPS via X-Forwarded-Proto or admin login
 * succeeds but /admin/users/me returns 401.
 * @see https://github.com/medusajs/medusa/issues/14550
 */
const forceHttpsProtocol = (
  req: MedusaRequest,
  _res: MedusaResponse,
  next: MedusaNextFunction
) => {
  if (process.env.NODE_ENV === "production") {
    Object.defineProperty(req, "protocol", {
      get: () => "https",
      configurable: true,
    })
    req.headers["x-forwarded-proto"] = "https"
  }

  next()
}

/**
 * `admin.path` stays `/app` (Medusa default). `path: "/"` is for a standalone
 * admin host — here the SPA catch-all would also take `/health` and `/store`.
 */
const redirectRootToAdmin = (
  req: MedusaRequest,
  res: MedusaResponse,
  next: MedusaNextFunction
) => {
  // Matcher `/*` makes req.path "/" for every request — use originalUrl.
  const path = (req.originalUrl || "/").split("?")[0]
  if (req.method === "GET" && path === "/") {
    res.redirect(302, "/app")
    return
  }

  next()
}

export default defineMiddlewares({
  routes: [
    {
      matcher: "/*",
      middlewares: [redirectRootToAdmin, forceHttpsProtocol],
    },
  ],
})
