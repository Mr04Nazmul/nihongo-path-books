import pg from 'pg';
import {readFile} from 'node:fs/promises';
const pool=new pg.Pool({connectionString:process.env.MIGRATION_DATABASE_URL||process.env.DATABASE_URL});
try { await pool.query(await readFile(new URL('../migrations/001_initial.sql',import.meta.url),'utf8')); console.log('Migration applied'); } finally {await pool.end();}
