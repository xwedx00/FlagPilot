
const { Client } = require('pg');
require('dotenv').config();

async function resetDb() {
    const client = new Client({
        connectionString: process.env.DATABASE_URL,
    });

    try {
        await client.connect();
        console.log('Connected to database...');

        console.log('Dropping public schema...');
        await client.query('DROP SCHEMA public CASCADE;');

        console.log('Recreating public schema...');
        await client.query('CREATE SCHEMA public;');

        console.log('✅ Database reset successfully.');
    } catch (err) {
        console.error('❌ Error resetting database:', err);
        process.exit(1);
    } finally {
        await client.end();
    }
}

resetDb();
