// Capture the local demo screens used in the project documentation.
// Start the app on http://127.0.0.1:8000 with DEMO_MODE=1, then run:
//   node scripts/capture_screenshots.mjs
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const base = process.env.APP_URL || "http://127.0.0.1:8000";
const output = "screenshots";
mkdirSync(output, { recursive: true });

const browser = await chromium.launch({ channel: "chrome" });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1000 },
});
const page = await context.newPage();

async function settle() {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
}

async function shot(name, fullPage = true) {
  await settle();
  await page.screenshot({ path: `${output}/${name}.png`, fullPage });
}

async function login(email, password) {
  await page.goto(base, { waitUntil: "networkidle" });
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: /^Sign in/ }).click();
  await page.waitForURL(/\?view=/);
  await settle();
}

async function logout() {
  await page.getByRole("button", { name: "Sign out" }).click();
  await page.waitForSelector("#email");
  await settle();
}

await page.goto(base, { waitUntil: "networkidle" });
await shot("audit-login");

await login("recruiter@demo.test", "RecruiterDemo!2026");
await shot("audit-dashboard");
await page.goto(`${base}/?view=candidates`);
await shot("audit-candidates");
await page.goto(`${base}/?view=opportunities`);
await shot("audit-publish");
await page.goto(`${base}/?view=applications`);
await shot("audit-applications");
await page.goto(`${base}/?view=matches`);
await shot("audit-matches");
await page.goto(`${base}/?view=compare`);
await shot("audit-compare");
await page.goto(`${base}/?view=evaluations`);
await shot("audit-evaluations");

await page.setViewportSize({ width: 390, height: 844 });
await page.goto(`${base}/?view=jobs`);
await shot("audit-dashboard-mobile");
await page.setViewportSize({ width: 1440, height: 1000 });

await logout();
await login("candidate@demo.test", "CandidateDemo!2026");
await page.goto(`${base}/?view=candidates`);
await shot("audit-profile");

await logout();
await login("auditor@demo.test", "AuditorDemo!2026");
await page.setViewportSize({ width: 390, height: 844 });
await shot("audit-mobile");

await browser.close();
console.log("Screenshots written to", output);
