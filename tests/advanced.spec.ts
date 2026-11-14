import { test, expect, type Page } from "@playwright/test";
async function login(page: Page, role = "recruiter") {
  await page.goto("/");
  await page.getByRole("button", { name: role, exact: true }).click();
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("button", { name: "Sign out" })).toBeVisible();
}

test("candidate evidence gap, application update and snapshot comparison", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await login(page);
  const job = "Python Application Developer";
  await page.getByRole("button", { name: "Create job" }).click();
  await page.getByLabel("Job title").fill(job);
  await page
    .getByLabel("Role description")
    .fill("Build tested Python backend services and SQL queries.");
  await page.getByLabel("Required skills", { exact: true }).fill("Python, SQL");
  await page.getByRole("button", { name: "Create job", exact: true }).click();
  await page.getByRole("link", { name: "Publish jobs" }).click();
  await page.getByRole("textbox", { name: "Search opportunities" }).fill(job);
  await page.getByRole("button", { name: "Publish job", exact: true }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "Job published" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "candidate");
  await page.getByRole("button", { name: "Add profile" }).click();
  const profile = "Python Developer - Project Experience";
  await page.getByLabel("Profile name").fill(profile);
  await page
    .getByLabel("Resume evidence")
    .fill(
      "Currently learning Python. No experience with SQL. Built React interfaces with CSS and HTML.",
    );
  await page.getByRole("button", { name: "Save profile", exact: true }).click();
  await page.getByRole("link", { name: "Job opportunities" }).click();
  await page.getByRole("textbox", { name: "Search opportunities" }).fill(job);
  await page
    .getByLabel("Profile to submit")
    .selectOption({ label: profile + " · v1" });
  await page.getByRole("button", { name: "Check skill evidence" }).click();
  await expect(page.getByText("learning", { exact: true })).toBeVisible();
  await expect(page.getByText("negated", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Apply with selected profile" })
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "Application submitted" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page);
  await page.getByRole("link", { name: "Publish jobs" }).click();
  await page.getByRole("textbox", { name: "Search opportunities" }).fill(job);
  await page.getByRole("button", { name: "Match applicants" }).click();
  await expect(
    page.getByRole("heading", { name: "Understand the match." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Evidence", exact: true }).click();
  await expect(page.getByText("learning", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "candidate");
  await page
    .getByRole("textbox", { name: "Search candidate profiles" })
    .fill(profile);
  await page.getByRole("button", { name: "Inspect", exact: true }).click();
  await page
    .getByLabel("Resume evidence")
    .fill(
      "Built Python services and SQL queries. Added pytest integration tests and used Git for code reviews.",
    );
  await page.getByRole("button", { name: "Save changes" }).click();
  await page.getByRole("link", { name: "Job opportunities" }).click();
  await page.getByRole("textbox", { name: "Search opportunities" }).fill(job);
  await expect(
    page.getByRole("button", { name: "Withdraw application" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "View application status" }).click();
  await expect(
    page.getByText("Awaiting recruiter response", { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page);
  await page.getByRole("link", { name: "Publish jobs" }).click();
  await page.getByRole("textbox", { name: "Search opportunities" }).fill(job);
  await page.getByRole("button", { name: "Match applicants" }).click();
  await expect(
    page.getByRole("heading", { name: "Understand the match." }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Compare snapshots" }).click();
  const options = await page.locator("#compare-left option").allTextContents();
  const matching = options.filter((t) => t.startsWith(job));
  expect(matching.length).toBe(2);
  await page
    .getByLabel("Earlier / baseline snapshot")
    .selectOption({ label: matching[1] });
  await page
    .getByLabel("Comparison snapshot")
    .selectOption({ label: matching[0] });
  await page
    .getByRole("button", { name: "Compare snapshots", exact: true })
    .click();
  await expect(page.getByRole("cell", { name: /v1.*v1 both/ })).toBeVisible();
  await page.screenshot({
    path: "docs/screenshots/snapshot-comparison-v2.png",
    fullPage: true,
  });
  await page.getByRole("link", { name: "Applications", exact: true }).click();
  await page
    .getByRole("button", { name: "Review application", exact: true })
    .first()
    .click();
  await page
    .getByLabel("Recruitment decision", { exact: true })
    .selectOption("accepted");
  await expect(
    page.getByRole("heading", { name: /Matching score:/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Feedback to candidate" }),
  ).toHaveCount(0);
  await expect(
    page.getByText(
      /Your application has been accepted for the next recruitment stage/,
    ),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Save recruitment decision", exact: true })
    .click();
  await expect(
    page.getByText("Accepted for next stage", { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "candidate");
  await page
    .getByRole("link", { name: "My applications", exact: true })
    .click();
  await expect(
    page.getByText(
      /Your application has been accepted for the next recruitment stage/,
    ),
  ).toBeVisible();
  await expect(page.getByText(/Matching evidence score:/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Withdraw", exact: true }),
  ).toHaveCount(0);
  expect(errors).toEqual([]);
});

test("measured TF-IDF and local semantic evaluation, export and auditor aggregates", async ({
  page,
}) => {
  test.setTimeout(120000);
  await login(page);
  await page.getByRole("link", { name: "Model evaluation" }).click();
  await page.getByRole("button", { name: "Load synthetic example" }).click();
  await expect(page.getByLabel("Labelled dataset JSON")).toHaveValue(
    /Synthetic relevance smoke test/,
  );
  await page.getByLabel("Methods to compare").selectOption("both");
  await page
    .getByRole("button", { name: "Run evaluation", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Run evaluation", exact: true }),
  ).toBeEnabled({ timeout: 90000 });
  await expect(
    page.getByRole("cell", { name: "skill-semantic-v2", exact: true }),
  ).toBeVisible({ timeout: 90000 });
  await expect(
    page.getByRole("cell", { name: "skill-tfidf-v2", exact: true }),
  ).toBeVisible();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export evaluation" }).click();
  expect((await download).suggestedFilename()).toContain("model-evaluation");
  await page.screenshot({
    path: "docs/screenshots/model-evaluation-v2.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Sign out" }).click();
  await login(page, "auditor");
  await page.getByRole("link", { name: "Model evaluation" }).click();
  await expect(
    page.getByRole("cell", { name: "skill-semantic-v2", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Run evaluation", exact: true }),
  ).toHaveCount(0);
});
