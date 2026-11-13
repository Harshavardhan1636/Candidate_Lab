import { defineConfig } from "@playwright/test";
import path from "node:path";
// Test records belong to a disposable database, never the live workspace.
const databaseFile =
  process.env.CANDIDATE_E2E_DB || path.resolve(`data/e2e-${Date.now()}.db`);
process.env.CANDIDATE_E2E_DB = databaseFile;
process.env.DATABASE_URL = `sqlite:///${databaseFile.replaceAll("\\", "/")}`;
process.env.DEMO_MODE = "1";
process.env.ALLOWED_ORIGINS = "http://127.0.0.1:8001";
process.env.SEMANTIC_MODEL_PATH = path.resolve("models/all-MiniLM-L6-v2");
process.env.HF_HOME = path.resolve("models/.hf");
process.env.HF_HUB_OFFLINE = "1";
export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  use: {
    baseURL: "http://127.0.0.1:8001",
    channel: "chrome",
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: {
    command: `"${path.resolve(".venv/Scripts/python.exe")}" -m uvicorn backend.app:app --host 127.0.0.1 --port 8001`,
    url: "http://127.0.0.1:8001/api/health",
    reuseExistingServer: false,
    timeout: 60000,
  },
});
