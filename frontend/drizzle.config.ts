import { config } from "dotenv"
import { defineConfig } from "drizzle-kit"

// Load .env.local for local development
config({ path: ".env.local" })

export default defineConfig({
    out: "./src/database/migrations",
    schema: "src/database/schema.ts",
    dialect: "postgresql",
    dbCredentials: {
        url: process.env.DATABASE_URL!
    }
})

