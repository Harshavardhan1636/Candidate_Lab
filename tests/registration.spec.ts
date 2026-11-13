import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import path from "node:path";

for (const role of ["candidate", "recruiter", "auditor"]) {
  test(`new ${role} registers and signs in`, async ({ page }) => {
    const email = `browser-${role}-${Date.now()}@example.test`;
    let code = "";
    if (role !== "candidate") {
      const output = execFileSync(
        path.resolve(".venv/Scripts/python.exe"),
        ["-m", "backend.invite", "--email", email, "--role", role],
        { encoding: "utf8" },
      );
      code = output.split(/\r?\n/)[1].trim();
    }
    await page.goto("/");
    await page.getByRole("button", { name: "Create a new account" }).click();
    await page.getByLabel("Account role").selectOption(role);
    if (role === "candidate") {
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: "screenshots/registration-mobile.png",
        fullPage: true,
      });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBeTruthy();
    }
    await page.getByLabel("Email", { exact: true }).fill(email);
    await page
      .getByLabel("New password", { exact: true })
      .fill("StrongPassword!2026");
    await page
      .getByLabel("Confirm password", { exact: true })
      .fill("mismatched");
    if (code) await page.getByLabel("Invitation code").fill(code);
    await page
      .getByRole("button", { name: "Create account", exact: true })
      .click();
    await expect(page.getByRole("alert")).toContainText(
      "Passwords do not match",
    );
    await page
      .getByLabel("Confirm password", { exact: true })
      .fill("StrongPassword!2026");
    await page
      .getByRole("button", { name: "Create account", exact: true })
      .click();
    await expect(
      page.getByText("Account created. Sign in with your new credentials.", {
        exact: true,
      }),
    ).toBeVisible();
    await expect(page.getByLabel("Email", { exact: true })).toHaveValue(email);
    await expect(page.getByLabel("Password", { exact: true })).toHaveValue("");
    await page
      .getByLabel("Password", { exact: true })
      .fill("StrongPassword!2026");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    const heading =
      role === "candidate"
        ? "Your profile, your evidence."
        : role === "recruiter"
          ? "Recruitment overview"
          : "Measure the differences.";
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  });
}
