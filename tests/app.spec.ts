import { test, expect, type Page } from "@playwright/test";
async function login(page: Page, role = "recruiter") {
  await page.goto("/");
  await page.getByRole("button", { name: role, exact: true }).click();
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
}
test("recruiter creates, corrects, matches and reviews evidence", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await login(page);
  await page.getByRole("button", { name: "Create job" }).click();
  await page.getByLabel("Job title").fill("Python Backend Engineer");
  await page
    .getByLabel("Role description")
    .fill(
      "Build reliable Python backend services and document the evidence for reviewers.",
    );
  await page.getByLabel("Required skills", { exact: true }).fill("Python, SQL");
  await page.getByLabel("Preferred skills", { exact: true }).fill("FastAPI");
  await page.getByRole("button", { name: "Create job", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Recruitment overview" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Candidate profiles" }).click();
  await expect(page.getByRole("button", { name: "Add profile" })).toHaveCount(
    0,
  );
  await page
    .getByRole("button", { name: "Inspect", exact: true })
    .first()
    .click();
  await expect(
    page.getByText("Read-only candidate information.", { exact: false }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Save changes" })).toHaveCount(
    0,
  );
  await expect(page.getByLabel("Resume evidence")).toHaveCount(0);
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "candidate");
  await page.getByRole("button", { name: "Add profile" }).click();
  const label = "Python Developer - API Testing";
  await page.getByLabel("Profile name").fill(label);
  await page.locator("#resume-file").setInputFiles({
    name: "resume.txt",
    mimeType: "text/plain",
    buffer: Buffer.from(
      "Developed Python REST APIs with FastAPI and PostgreSQL. Added pytest integration tests and deployed Docker services.",
    ),
  });
  await expect(page.getByLabel("Resume evidence")).toHaveValue(
    /Developed Python/,
  );
  await page.getByRole("button", { name: "Save profile", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Search candidate profiles" })
    .fill(label);
  await page.getByRole("button", { name: "Inspect", exact: true }).click();
  await page
    .getByLabel("Resume evidence")
    .fill(
      "Developed Python REST APIs with FastAPI and PostgreSQL. Added pytest integration tests and Git reviews using Docker.",
    );
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(
    page.getByRole("heading", { name: "Your profile, your evidence." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page);
  await page.getByRole("link", { name: "Publish jobs" }).click();
  await page
    .getByRole("button", { name: "Publish job", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "Job published" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "candidate");
  await page.getByRole("link", { name: "Job opportunities" }).click();
  await page
    .getByRole("button", { name: "Apply with selected profile" })
    .first()
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "Application submitted" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page);
  await page.getByRole("link", { name: "Job details" }).click();
  await page.getByRole("button", { name: "Run matching" }).first().click();
  await expect(
    page.getByRole("heading", { name: "Understand the match." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Evidence", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Requirement → evidence" }),
  ).toBeVisible();
  await page
    .getByLabel("Job-related reason")
    .fill(
      "Strong supporting evidence for Python and SQL; further interview assessment required.",
    );
  await page.getByRole("button", { name: "Save review" }).click();
  await expect(
    page.getByText("Last human review", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "screenshots/evidence-desktop.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
test("auditor aggregate export, keyboard controls and narrow layout", async ({
  page,
}) => {
  await login(page, "auditor");
  await expect(
    page.getByRole("heading", { name: "Measure the differences." }),
  ).toBeVisible();
  const seedReport = (
    await page.locator("#audit-run option").allTextContents()
  ).find((t) => t.startsWith("Backend Engineer"));
  await page
    .getByLabel("Matching snapshot")
    .selectOption({ label: seedReport! });
  await expect(page.getByText("Cohort A", { exact: true })).toBeVisible();
  await page.getByLabel("Common score cutoff:", { exact: false }).focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#threshold")).toHaveValue("65");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export report" }).click();
  expect((await download).suggestedFilename()).toContain("cohort-audit");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "screenshots/audit-mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("link", { name: "Audit trail" }).click();
  await expect(
    page.getByRole("heading", { name: "A record of the work." }),
  ).toBeVisible();
});
test("invalid credentials and unsaved changes preserve input", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Password", { exact: true }).fill("invalid-password");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("incorrect");
  await page.getByRole("button", { name: "recruiter", exact: true }).click();
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await page.getByRole("button", { name: "Create job" }).click();
  await page.getByLabel("Job title").fill("Keep this draft");
  await page.getByRole("link", { name: "Candidate profiles" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByLabel("Job title")).toHaveValue("Keep this draft");
  await page.getByRole("button", { name: "Create job", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator("#description")).toHaveAttribute(
    "aria-invalid",
    "true",
  );
  await page.goBack();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button", { name: "Keep editing" }).click();
  await expect(page.getByLabel("Job title")).toHaveValue("Keep this draft");
});

test("candidate sees own profile and cannot navigate to recruiter views", async ({
  page,
}) => {
  await login(page, "candidate");
  await page
    .getByRole("textbox", { name: "Search candidate profiles" })
    .fill("Python Developer - Inventory APIs");
  await expect(
    page.getByRole("heading", { name: "Your profile, your evidence." }),
  ).toBeVisible();
  await expect(
    page.getByText("Python Developer - Inventory APIs", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Python Developer - Data Pipelines", { exact: true }),
  ).toHaveCount(0);
  await page.goto("/?view=matches");
  await expect(
    page.getByRole("heading", {
      name: "This view is not available for your role",
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Matching evidence" }),
  ).toHaveCount(0);
});
