import express from "express";
import { createServer as createViteServer } from "vite";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import cookieParser from "cookie-parser";
import multer from "multer";
import cors from "cors";
import { z } from "zod";
import { EVENTS, MOCK_USER } from "./constants.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const db = new Database("database.sqlite");
const JWT_SECRET = process.env.JWT_SECRET || "super-secret-key-change-me";

// Initialize Database
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatarUrl TEXT,
    username TEXT UNIQUE,
    bio TEXT,
    phone TEXT,
    location TEXT,
    interests TEXT,
    onboardingCompleted INTEGER DEFAULT 0,
    savedEventIds TEXT DEFAULT '[]',
    attendedEventIds TEXT DEFAULT '[]',
    hostedEventIds TEXT DEFAULT '[]',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Migration: Ensure all columns exist (for existing databases)
const tableInfo = db.prepare("PRAGMA table_info(users)").all() as any[];
const columns = tableInfo.map(c => c.name);

const requiredColumns = [
  { name: 'password_hash', type: 'TEXT NOT NULL DEFAULT ""' },
  { name: 'avatarUrl', type: 'TEXT' },
  { name: 'username', type: 'TEXT UNIQUE' },
  { name: 'bio', type: 'TEXT' },
  { name: 'phone', type: 'TEXT' },
  { name: 'location', type: 'TEXT' },
  { name: 'interests', type: 'TEXT' },
  { name: 'onboardingCompleted', type: 'INTEGER DEFAULT 0' }
];

for (const col of requiredColumns) {
  if (!columns.includes(col.name)) {
    try {
      db.exec(`ALTER TABLE users ADD COLUMN ${col.name} ${col.type}`);
      console.log(`Added column ${col.name} to users table`);
    } catch (err) {
      console.error(`Failed to add column ${col.name}:`, err);
    }
  }
}

db.exec(`
  CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    location TEXT NOT NULL,
    venueName TEXT,
    format TEXT NOT NULL,
    imageUrl TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    hostId TEXT NOT NULL,
    sponsorId TEXT,
    attendees INTEGER DEFAULT 0,
    capacity INTEGER NOT NULL,
    tags TEXT,
    isFeatured INTEGER DEFAULT 0,
    sponsorshipSettings TEXT,
    visibility TEXT DEFAULT 'public',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// Migration: Ensure events table columns exist
const eventTableInfo = db.prepare("PRAGMA table_info(events)").all() as any[];
const eventColumns = eventTableInfo.map((c: any) => c.name);

const eventRequiredColumns = [
  { name: 'visibility', type: 'TEXT DEFAULT "public"' },
  { name: 'createdAt', type: 'DATETIME' },
  { name: 'updatedAt', type: 'DATETIME' }
];

for (const col of eventRequiredColumns) {
  if (!eventColumns.includes(col.name)) {
    try {
      db.exec(`ALTER TABLE events ADD COLUMN ${col.name} ${col.type}`);
    } catch (err) {
      console.error(`Failed to add column ${col.name}:`, err);
    }
  }
}

db.exec(`
  CREATE TABLE IF NOT EXISTS event_attendees (
    eventId TEXT NOT NULL,
    userId TEXT NOT NULL,
    joinedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (eventId, userId)
  );
`);

db.exec(`
  CREATE TABLE IF NOT EXISTS sponsor_profiles (
    userId TEXT PRIMARY KEY,
    companyName TEXT NOT NULL,
    website TEXT,
    bio TEXT,
    industries TEXT DEFAULT '[]',
    budgetMin REAL DEFAULT 0,
    budgetMax REAL DEFAULT 0,
    preferredFormats TEXT DEFAULT '[]',
    preferredGeographies TEXT DEFAULT '[]',
    preferredAudienceTypes TEXT DEFAULT '[]',
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

db.exec(`
  CREATE TABLE IF NOT EXISTS sponsorship_proposals (
    id TEXT PRIMARY KEY,
    eventId TEXT NOT NULL,
    eventTitle TEXT NOT NULL,
    senderId TEXT NOT NULL,
    senderName TEXT NOT NULL,
    receiverId TEXT NOT NULL,
    message TEXT NOT NULL,
    proposalType TEXT NOT NULL DEFAULT 'sponsorship',
    status TEXT NOT NULL DEFAULT 'pending',
    timestamp INTEGER NOT NULL,
    estimatedInvestment REAL NOT NULL,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

const proposalTableInfo = db.prepare("PRAGMA table_info(sponsorship_proposals)").all() as any[];
const proposalColumns = proposalTableInfo.map((c: any) => c.name);
if (!proposalColumns.includes('proposalType')) {
  try {
    db.exec(`ALTER TABLE sponsorship_proposals ADD COLUMN proposalType TEXT NOT NULL DEFAULT 'sponsorship'`);
  } catch (err) {
    console.error('Failed to add proposalType column:', err);
  }
}

const safeParseJsonArray = (value: any): string[] => {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const computeSponsorEventMatch = (event: any, sponsorProfile: any) => {
  const industries = safeParseJsonArray(sponsorProfile.industries).map((i) => i.toLowerCase());
  const preferredFormats = safeParseJsonArray(sponsorProfile.preferredFormats).map((f) => f.toLowerCase());
  const preferredGeographies = safeParseJsonArray(sponsorProfile.preferredGeographies).map((g) => g.toLowerCase());
  const preferredAudienceTypes = safeParseJsonArray(sponsorProfile.preferredAudienceTypes).map((a) => a.toLowerCase());

  const reasons: string[] = [];
  let score = 45;

  if (industries.includes(String(event.category || '').toLowerCase())) {
    score += 25;
    reasons.push(`Strong industry fit (${event.category})`);
  }

  if (preferredFormats.includes(String(event.format || '').toLowerCase())) {
    score += 15;
    reasons.push(`Preferred format (${event.format})`);
  }

  const location = String(event.location || '').toLowerCase();
  if (preferredGeographies.some((geo) => geo && location.includes(geo))) {
    score += 10;
    reasons.push('Location aligns with target geography');
  }

  const audienceType = String(event.sponsorshipSettings?.audience_type || '').toLowerCase();
  if (audienceType && preferredAudienceTypes.includes(audienceType)) {
    score += 10;
    reasons.push('Audience profile match');
  }

  if (!reasons.length) {
    reasons.push('General sponsorship compatibility');
  }

  return {
    score: Math.max(0, Math.min(100, score)),
    reason: reasons.join(' • ')
  };
};

// Seed Database
const userCount = db.prepare("SELECT count(*) as count FROM users").get() as any;
if (userCount.count === 0) {
  const passwordHash = bcrypt.hashSync("password123", 10);
  const stmt = db.prepare(`
    INSERT INTO users (id, name, email, password_hash, avatarUrl, savedEventIds, attendedEventIds, hostedEventIds)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    MOCK_USER.id,
    MOCK_USER.name,
    MOCK_USER.email,
    passwordHash,
    MOCK_USER.avatarUrl,
    JSON.stringify(MOCK_USER.savedEventIds),
    JSON.stringify(MOCK_USER.attendedEventIds),
    JSON.stringify(MOCK_USER.hostedEventIds)
  );
}

const eventCount = db.prepare("SELECT count(*) as count FROM events").get() as any;
if (eventCount.count === 0) {
  const stmt = db.prepare(`
    INSERT INTO events (
      id, title, description, date, time, location, venueName, format, 
      imageUrl, price, category, hostId, sponsorId, attendees, capacity, 
      tags, isFeatured, sponsorshipSettings, visibility, createdAt, updatedAt
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'public', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
  `);

  for (const event of EVENTS) {
    // Update dates to be in the future for the demo
    const futureDate = event.date.replace('2025', '2026');
    stmt.run(
      event.id,
      event.title,
      event.description,
      futureDate,
      event.time,
      event.location,
      event.venueName || null,
      event.format,
      event.imageUrl || null,
      event.price,
      event.category,
      event.hostId,
      event.sponsorId || null,
      event.attendees || 0,
      event.capacity,
      JSON.stringify(event.tags || []),
      event.isFeatured ? 1 : 0,
      JSON.stringify(event.sponsorshipSettings || null)
    );
  }
}

const seededSponsors = [
  {
    user: {
      id: 'sp1',
      name: 'Maya Chen',
      email: 'maya@techflow.com',
      avatarUrl: 'https://picsum.photos/seed/sponsor1/200'
    },
    profile: {
      companyName: 'TechFlow Ventures',
      website: 'https://example.com/techflow',
      bio: 'Early-stage technology investor and growth partner focused on AI, developer tools, and community-led products.',
      industries: ['Tech', 'AI', 'Developer Tools'],
      budgetMin: 2000,
      budgetMax: 25000,
      preferredFormats: ['Online', 'Hybrid'],
      preferredGeographies: ['san francisco', 'new york', 'online'],
      preferredAudienceTypes: ['professionals', 'founders_operators']
    }
  },
  {
    user: {
      id: 'sp2',
      name: 'Jordan Blake',
      email: 'jordan@nebulaenergy.com',
      avatarUrl: 'https://picsum.photos/seed/sponsor2/200'
    },
    profile: {
      companyName: 'Nebula Energy',
      website: 'https://example.com/nebula',
      bio: 'Lifestyle and sports beverage brand partnering with high-attendance events and experiential activations.',
      industries: ['Sports', 'Lifestyle', 'Consumer'],
      budgetMin: 1500,
      budgetMax: 12000,
      preferredFormats: ['In-Person', 'Hybrid'],
      preferredGeographies: ['las vegas', 'los angeles', 'miami'],
      preferredAudienceTypes: ['general_public', 'students_earlycareer']
    }
  },
  {
    user: {
      id: 'sp3',
      name: 'Priya Nair',
      email: 'priya@artspark.media',
      avatarUrl: 'https://picsum.photos/seed/sponsor3/200'
    },
    profile: {
      companyName: 'ArtSpark Media',
      website: 'https://example.com/artspark',
      bio: 'Creative media collective supporting arts, culture, and community storytelling events.',
      industries: ['Art', 'Culture', 'Media'],
      budgetMin: 800,
      budgetMax: 9000,
      preferredFormats: ['In-Person', 'Online'],
      preferredGeographies: ['new york', 'chicago', 'remote'],
      preferredAudienceTypes: ['general_public', 'professionals']
    }
  }
];

const sponsorUserInsertStmt = db.prepare(`
  INSERT OR IGNORE INTO users (
    id, name, email, password_hash, avatarUrl, savedEventIds, attendedEventIds, hostedEventIds, onboardingCompleted
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
`);

const sponsorProfileUpsertStmt = db.prepare(`
  INSERT INTO sponsor_profiles (
    userId, companyName, website, bio, industries, budgetMin, budgetMax,
    preferredFormats, preferredGeographies, preferredAudienceTypes, createdAt, updatedAt
  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
  ON CONFLICT(userId) DO UPDATE SET
    companyName = excluded.companyName,
    website = excluded.website,
    bio = excluded.bio,
    industries = excluded.industries,
    budgetMin = excluded.budgetMin,
    budgetMax = excluded.budgetMax,
    preferredFormats = excluded.preferredFormats,
    preferredGeographies = excluded.preferredGeographies,
    preferredAudienceTypes = excluded.preferredAudienceTypes,
    updatedAt = CURRENT_TIMESTAMP
`);

for (const sponsor of seededSponsors) {
  const sponsorPasswordHash = bcrypt.hashSync('password123', 10);
  sponsorUserInsertStmt.run(
    sponsor.user.id,
    sponsor.user.name,
    sponsor.user.email,
    sponsorPasswordHash,
    sponsor.user.avatarUrl,
    JSON.stringify([]),
    JSON.stringify([]),
    JSON.stringify([]),
    1
  );

  sponsorProfileUpsertStmt.run(
    sponsor.user.id,
    sponsor.profile.companyName,
    sponsor.profile.website,
    sponsor.profile.bio,
    JSON.stringify(sponsor.profile.industries),
    sponsor.profile.budgetMin,
    sponsor.profile.budgetMax,
    JSON.stringify(sponsor.profile.preferredFormats),
    JSON.stringify(sponsor.profile.preferredGeographies),
    JSON.stringify(sponsor.profile.preferredAudienceTypes)
  );
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.set('trust proxy', 1);
  app.use(cors({
    origin: (origin, callback) => {
      // In development/preview, we want to allow the origin of the request
      // to support credentials (cookies)
      if (!origin) {
        callback(null, true);
      } else {
        callback(null, origin);
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    exposedHeaders: ['Set-Cookie']
  }));
  app.use(cookieParser());
  app.use(express.json());

  // Debug route to check cookies
  app.get("/api/debug/cookies", (req, res) => {
    res.json({
      cookies: req.cookies,
      headers: req.headers,
      trustProxy: app.get('trust proxy')
    });
  });

  // Multer setup for avatar uploads
  const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      cb(null, 'public/uploads/');
    },
    filename: (req, file, cb) => {
      const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
      cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
  });
  const upload = multer({ storage });

  // Auth Middleware
  const authenticate = (req: any, res: any, next: any) => {
    const token = req.cookies.token;
    console.log(`[Auth] Attempting access to ${req.path}. Token present: ${!!token}`);

    if (!token) {
      console.log("[Auth] Failed: No token in cookies. Headers:", JSON.stringify(req.headers));
      return res.status(401).json({ error: "Unauthorized: No token provided" });
    }
    try {
      const decoded = jwt.verify(token, JWT_SECRET) as any;
      req.userId = decoded.userId;
      next();
    } catch (error) {
      console.log("[Auth] Failed: Invalid token");
      res.status(401).json({ error: "Unauthorized: Invalid token" });
    }
  };

  const optionalAuthenticate = (req: any, res: any, next: any) => {
    const token = req.cookies.token;
    if (token) {
      try {
        const decoded = jwt.verify(token, JWT_SECRET) as any;
        req.userId = decoded.userId;
      } catch (error) { }
    }
    next();
  };

  // Auth Routes
  app.post("/api/auth/register", async (req, res) => {
    const schema = z.object({
      name: z.string().min(2),
      email: z.string().email(),
      password: z.string().min(8),
    });

    try {
      const { name, email, password } = schema.parse(req.body);
      const existingUser = db.prepare("SELECT * FROM users WHERE email = ?").get(email);
      if (existingUser) return res.status(400).json({ error: "Email already registered" });

      const id = Math.random().toString(36).substr(2, 9);
      const passwordHash = await bcrypt.hash(password, 10);

      db.prepare(`
        INSERT INTO users (id, name, email, password_hash)
        VALUES (?, ?, ?, ?)
      `).run(id, name, email, passwordHash);

      const token = jwt.sign({ userId: id }, JWT_SECRET, { expiresIn: '7d' });

      const isProduction = process.env.NODE_ENV === 'production';
      const cookieOptions: any = {
        httpOnly: true,
        secure: isProduction,
        sameSite: isProduction ? 'none' : 'lax',
        maxAge: 7 * 24 * 60 * 60 * 1000,
        path: '/',
      };

      if (isProduction) cookieOptions.partitioned = true;

      res.cookie('token', token, cookieOptions);
      console.log(`[Auth] Registration successful for user ${id}. Cookie set with options:`, JSON.stringify(cookieOptions));

      const user = db.prepare("SELECT * FROM users WHERE id = ?").get(id) as any;
      const { password_hash: _, ...userWithoutPassword } = user;

      const attendedEventRows = db.prepare("SELECT eventId FROM event_attendees WHERE userId = ?").all(id) as any[];

      res.status(201).json({
        user: {
          ...userWithoutPassword,
          savedEventIds: JSON.parse(user.savedEventIds || '[]'),
          attendedEventIds: attendedEventRows.map((r) => r.eventId),
          hostedEventIds: JSON.parse(user.hostedEventIds || '[]'),
          interests: JSON.parse(user.interests || '[]'),
          onboardingCompleted: !!user.onboardingCompleted
        }
      });
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post("/api/auth/login", async (req, res) => {
    const { email, password } = req.body;
    const user = db.prepare("SELECT * FROM users WHERE email = ?").get(email) as any;
    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' });

    const isProduction = process.env.NODE_ENV === 'production';
    const cookieOptions: any = {
      httpOnly: true,
      secure: isProduction,
      sameSite: isProduction ? 'none' : 'lax',
      maxAge: 7 * 24 * 60 * 60 * 1000,
      path: '/',
    };

    if (isProduction) cookieOptions.partitioned = true;

    res.cookie('token', token, cookieOptions);
    console.log(`[Auth] Login successful for user ${user.id}. Cookie set.`);

    const { password_hash, ...userWithoutPassword } = user;

    const attendedEventRows = db.prepare("SELECT eventId FROM event_attendees WHERE userId = ?").all(user.id) as any[];

    res.json({
      user: {
        ...userWithoutPassword,
        savedEventIds: JSON.parse(user.savedEventIds || '[]'),
        attendedEventIds: attendedEventRows.map((r) => r.eventId),
        hostedEventIds: JSON.parse(user.hostedEventIds || '[]'),
        interests: JSON.parse(user.interests || '[]'),
        onboardingCompleted: !!user.onboardingCompleted
      }
    });
  });

  app.post("/api/auth/logout", (req, res) => {
    const isProduction = process.env.NODE_ENV === 'production';
    res.clearCookie('token', {
      httpOnly: true,
      secure: isProduction,
      sameSite: isProduction ? 'none' : 'lax',
      path: '/',
    });
    res.json({ success: true });
  });

  app.get("/api/auth/me", authenticate, (req: any, res) => {
    const user = db.prepare("SELECT * FROM users WHERE id = ?").get(req.userId) as any;
    if (!user) return res.status(404).json({ error: "User not found" });

    const { password_hash, ...userWithoutPassword } = user;

    const attendedEventRows = db.prepare("SELECT eventId FROM event_attendees WHERE userId = ?").all(user.id) as any[];

    res.json({
      ...userWithoutPassword,
      savedEventIds: JSON.parse(user.savedEventIds || '[]'),
      attendedEventIds: attendedEventRows.map((r) => r.eventId),
      hostedEventIds: JSON.parse(user.hostedEventIds || '[]'),
      interests: JSON.parse(user.interests || '[]'),
      onboardingCompleted: !!user.onboardingCompleted
    });
  });

  // Profile Routes
  app.put("/api/profile", authenticate, (req: any, res) => {
    const schema = z.object({
      username: z.string().min(3).optional(),
      bio: z.string().max(500).optional(),
      phone: z.string().optional(),
      location: z.string().optional(),
      interests: z.array(z.string()).optional(),
      onboardingCompleted: z.boolean().optional()
    });

    try {
      const data = schema.parse(req.body);
      const updates: string[] = [];
      const values: any[] = [];

      for (const [key, val] of Object.entries(data)) {
        if (key === 'interests') {
          updates.push(`interests = ?`);
          values.push(JSON.stringify(val));
        } else if (key === 'onboardingCompleted') {
          updates.push(`onboardingCompleted = ?`);
          values.push(val ? 1 : 0);
        } else {
          updates.push(`${key} = ?`);
          values.push(val);
        }
      }

      if (updates.length > 0) {
        db.prepare(`UPDATE users SET ${updates.join(', ')} WHERE id = ?`).run(...values, req.userId);
      }
      res.json({ success: true });
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post("/api/profile/avatar", authenticate, upload.single('avatar'), (req: any, res) => {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });
    const avatarUrl = `/uploads/${req.file.filename}`;
    db.prepare("UPDATE users SET avatarUrl = ? WHERE id = ?").run(avatarUrl, req.userId);
    res.json({ avatarUrl });
  });

  // Sponsor Routes
  app.get("/api/sponsors", optionalAuthenticate, (req: any, res) => {
    try {
      const eventId = req.query.eventId as string | undefined;

      const sponsors = db.prepare(`
        SELECT u.id as userId, u.name, u.email, u.avatarUrl,
               sp.companyName, sp.website, sp.bio, sp.industries, sp.budgetMin, sp.budgetMax,
               sp.preferredFormats, sp.preferredGeographies, sp.preferredAudienceTypes
        FROM sponsor_profiles sp
        JOIN users u ON u.id = sp.userId
        ORDER BY sp.updatedAt DESC
      `).all() as any[];

      let parsedSponsors = sponsors.map((s) => ({
        ...s,
        industries: safeParseJsonArray(s.industries),
        preferredFormats: safeParseJsonArray(s.preferredFormats),
        preferredGeographies: safeParseJsonArray(s.preferredGeographies),
        preferredAudienceTypes: safeParseJsonArray(s.preferredAudienceTypes)
      }));

      if (eventId) {
        const event = db.prepare("SELECT * FROM events WHERE id = ?").get(eventId) as any;
        if (!event) return res.status(404).json({ error: "Event not found" });

        const parsedEvent = {
          ...event,
          sponsorshipSettings: event.sponsorshipSettings ? JSON.parse(event.sponsorshipSettings) : undefined
        };

        parsedSponsors = parsedSponsors
          .map((s) => {
            const match = computeSponsorEventMatch(parsedEvent, s);
            return {
              ...s,
              matchScore: match.score,
              matchReason: match.reason
            };
          })
          .sort((a, b) => b.matchScore - a.matchScore);
      }

      res.json(parsedSponsors);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/sponsors/me", authenticate, (req: any, res) => {
    try {
      const sponsorProfile = db.prepare("SELECT * FROM sponsor_profiles WHERE userId = ?").get(req.userId) as any;
      if (!sponsorProfile) return res.status(404).json({ error: "Sponsor profile not found" });

      res.json({
        ...sponsorProfile,
        industries: safeParseJsonArray(sponsorProfile.industries),
        preferredFormats: safeParseJsonArray(sponsorProfile.preferredFormats),
        preferredGeographies: safeParseJsonArray(sponsorProfile.preferredGeographies),
        preferredAudienceTypes: safeParseJsonArray(sponsorProfile.preferredAudienceTypes)
      });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/sponsors/signup", authenticate, (req: any, res) => {
    const schema = z.object({
      companyName: z.string().min(2),
      website: z.string().url().optional().or(z.literal('')),
      bio: z.string().max(800).optional().or(z.literal('')),
      industries: z.array(z.string()).min(1),
      budgetMin: z.number().min(0),
      budgetMax: z.number().min(0),
      preferredFormats: z.array(z.enum(['Online', 'In-Person', 'Hybrid'])).optional().default([]),
      preferredGeographies: z.array(z.string()).optional().default([]),
      preferredAudienceTypes: z.array(z.enum(['general_public', 'students_earlycareer', 'professionals', 'founders_operators', 'executives_investors'])).optional().default([])
    }).refine((data) => data.budgetMax >= data.budgetMin, {
      message: 'budgetMax must be greater than or equal to budgetMin',
      path: ['budgetMax']
    });

    try {
      const data = schema.parse(req.body);

      db.prepare(`
        INSERT INTO sponsor_profiles (
          userId, companyName, website, bio, industries, budgetMin, budgetMax,
          preferredFormats, preferredGeographies, preferredAudienceTypes, createdAt, updatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(userId) DO UPDATE SET
          companyName = excluded.companyName,
          website = excluded.website,
          bio = excluded.bio,
          industries = excluded.industries,
          budgetMin = excluded.budgetMin,
          budgetMax = excluded.budgetMax,
          preferredFormats = excluded.preferredFormats,
          preferredGeographies = excluded.preferredGeographies,
          preferredAudienceTypes = excluded.preferredAudienceTypes,
          updatedAt = CURRENT_TIMESTAMP
      `).run(
        req.userId,
        data.companyName,
        data.website || null,
        data.bio || null,
        JSON.stringify(data.industries),
        data.budgetMin,
        data.budgetMax,
        JSON.stringify(data.preferredFormats),
        JSON.stringify(data.preferredGeographies),
        JSON.stringify(data.preferredAudienceTypes)
      );

      const profile = db.prepare("SELECT * FROM sponsor_profiles WHERE userId = ?").get(req.userId) as any;
      res.status(201).json({
        ...profile,
        industries: safeParseJsonArray(profile.industries),
        preferredFormats: safeParseJsonArray(profile.preferredFormats),
        preferredGeographies: safeParseJsonArray(profile.preferredGeographies),
        preferredAudienceTypes: safeParseJsonArray(profile.preferredAudienceTypes)
      });
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.get("/api/sponsors/matches", authenticate, (req: any, res) => {
    try {
      const profile = db.prepare("SELECT * FROM sponsor_profiles WHERE userId = ?").get(req.userId) as any;
      if (!profile) return res.status(404).json({ error: "Sponsor profile not found" });

      const now = new Date().toISOString().split('T')[0];
      const events = db.prepare(`
        SELECT events.*, users.name as hostName
        FROM events
        LEFT JOIN users ON events.hostId = users.id
        WHERE events.date >= ? AND events.visibility = 'public' AND events.hostId != ?
      `).all(now, req.userId) as any[];

      const matches = events
        .map((event) => {
          const parsedEvent = {
            ...event,
            tags: event.tags ? JSON.parse(event.tags) : [],
            sponsorshipSettings: event.sponsorshipSettings ? JSON.parse(event.sponsorshipSettings) : undefined
          };
          const match = computeSponsorEventMatch(parsedEvent, profile);
          return {
            ...parsedEvent,
            matchScore: match.score,
            matchReason: match.reason
          };
        })
        .sort((a, b) => b.matchScore - a.matchScore);

      res.json(matches);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  // Sponsorship Proposal Routes
  app.get("/api/proposals", authenticate, (req: any, res) => {
    try {
      const proposals = db.prepare(`
        SELECT * FROM sponsorship_proposals
        WHERE senderId = ? OR receiverId = ?
        ORDER BY timestamp DESC
      `).all(req.userId, req.userId);

      res.json(proposals);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/proposals", authenticate, (req: any, res) => {
    const schema = z.object({
      eventId: z.string().min(1),
      eventTitle: z.string().min(1),
      receiverId: z.string().min(1),
      message: z.string().min(10),
      estimatedInvestment: z.number().nonnegative(),
      proposalType: z.enum(['sponsorship', 'partnership']).optional().default('sponsorship')
    });

    try {
      const data = schema.parse(req.body);
      const sender = db.prepare("SELECT id, name FROM users WHERE id = ?").get(req.userId) as any;
      if (!sender) return res.status(404).json({ error: "Sender not found" });

      const receiver = db.prepare("SELECT id FROM users WHERE id = ?").get(data.receiverId) as any;
      if (!receiver) return res.status(404).json({ error: "Receiver not found" });

      const event = db.prepare("SELECT id, hostId, title FROM events WHERE id = ?").get(data.eventId) as any;
      if (!event) return res.status(404).json({ error: "Event not found" });
      if (data.proposalType === 'sponsorship') {
        if (event.hostId !== data.receiverId) {
          return res.status(400).json({ error: "Receiver must be the host of this event" });
        }
      } else {
        if (event.hostId !== req.userId) {
          return res.status(403).json({ error: "Only event hosts can send partnership requests" });
        }
        const sponsorProfile = db.prepare("SELECT userId FROM sponsor_profiles WHERE userId = ?").get(data.receiverId) as any;
        if (!sponsorProfile) {
          return res.status(400).json({ error: "Receiver must have an active sponsor profile" });
        }
      }

      const proposalId = Math.random().toString(36).substring(2, 11);
      const proposalTimestamp = Date.now();

      db.prepare(`
        INSERT INTO sponsorship_proposals (
          id, eventId, eventTitle, senderId, senderName, receiverId, message, proposalType, status, timestamp, estimatedInvestment, createdAt, updatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      `).run(
        proposalId,
        data.eventId,
        data.eventTitle,
        sender.id,
        sender.name,
        data.receiverId,
        data.message,
        data.proposalType,
        proposalTimestamp,
        data.estimatedInvestment
      );

      const createdProposal = db.prepare("SELECT * FROM sponsorship_proposals WHERE id = ?").get(proposalId);
      res.status(201).json(createdProposal);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.put("/api/proposals/:id/status", authenticate, (req: any, res) => {
    const schema = z.object({
      status: z.enum(['accepted', 'declined'])
    });

    try {
      const { status } = schema.parse(req.body);
      const proposal = db.prepare("SELECT * FROM sponsorship_proposals WHERE id = ?").get(req.params.id) as any;

      if (!proposal) return res.status(404).json({ error: "Proposal not found" });
      if (proposal.receiverId !== req.userId) {
        return res.status(403).json({ error: "Only the receiver can update proposal status" });
      }
      if (proposal.status !== 'pending') {
        return res.status(400).json({ error: "Proposal status has already been finalized" });
      }

      db.prepare(`
        UPDATE sponsorship_proposals
        SET status = ?, updatedAt = CURRENT_TIMESTAMP
        WHERE id = ?
      `).run(status, req.params.id);

      const updatedProposal = db.prepare("SELECT * FROM sponsorship_proposals WHERE id = ?").get(req.params.id);
      res.json(updatedProposal);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  // API Routes
  app.get("/api/events", optionalAuthenticate, (req: any, res) => {
    try {
      const now = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      let events;
      if (req.userId) {
        // Fetch all public events or events hosted by the logged-in user
        events = db.prepare("SELECT events.*, users.name as hostName FROM events LEFT JOIN users ON events.hostId = users.id WHERE events.date >= ? AND (events.visibility = 'public' OR events.hostId = ?)").all(now, req.userId);
      } else {
        events = db.prepare("SELECT events.*, users.name as hostName FROM events LEFT JOIN users ON events.hostId = users.id WHERE events.date >= ? AND events.visibility = 'public'").all(now);
      }

      const parsedEvents = events.map((e: any) => ({
        ...e,
        isFeatured: !!e.isFeatured,
        tags: e.tags ? JSON.parse(e.tags) : [],
        sponsorshipSettings: e.sponsorshipSettings ? JSON.parse(e.sponsorshipSettings) : undefined
      }));
      res.json(parsedEvents);
    } catch (err: any) { res.status(500).json({ error: err.message }); }
  });

  app.post("/api/events", authenticate, (req: any, res) => {
    const event = req.body;
    const hostId = req.userId; // Enforce owner logic
    const id = event.id || Math.random().toString(36).substr(2, 9);
    const visibility = event.visibility || 'public';

    const stmt = db.prepare(`
      INSERT INTO events (
        id, title, description, date, time, location, venueName, format, 
        imageUrl, price, category, hostId, sponsorId, attendees, capacity, 
        tags, isFeatured, sponsorshipSettings, visibility, createdAt, updatedAt
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    `);

    try {
      stmt.run(
        id, event.title, event.description, event.date, event.time, event.location,
        event.venueName || null, event.format, event.imageUrl || null, event.price || 0,
        event.category, hostId, event.sponsorId || null, event.attendees || 0, event.capacity,
        JSON.stringify(event.tags || []), event.isFeatured ? 1 : 0,
        event.sponsorshipSettings ? JSON.stringify(event.sponsorshipSettings) : null,
        visibility
      );
      res.status(201).json({ success: true, eventId: id });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/events/:id", optionalAuthenticate, (req: any, res) => {
    try {
      const event = db.prepare("SELECT events.*, users.name as hostName FROM events LEFT JOIN users ON events.hostId = users.id WHERE events.id = ?").get(req.params.id) as any;
      if (!event) return res.status(404).json({ error: "Event not found" });

      // Enforce visibility check
      if (event.visibility !== 'public' && event.hostId !== req.userId) {
        return res.status(403).json({ error: "Access denied: This event is private" });
      }

      res.json({
        ...event,
        isFeatured: !!event.isFeatured,
        tags: event.tags ? JSON.parse(event.tags) : [],
        sponsorshipSettings: event.sponsorshipSettings ? JSON.parse(event.sponsorshipSettings) : undefined
      });
    } catch (err: any) { res.status(500).json({ error: err.message }); }
  });

  app.get("/api/events/:id/attendees", authenticate, (req: any, res) => {
    try {
      const event = db.prepare("SELECT * FROM events WHERE id = ?").get(req.params.id) as any;
      if (!event) return res.status(404).json({ error: "Event not found" });

      // Enforce owner check
      if (event.hostId !== req.userId) {
        return res.status(403).json({ error: "Access denied: Only the host can view attendees" });
      }

      const attendees = db.prepare(`
        SELECT u.id, u.name, u.username, u.avatarUrl, ea.joinedAt
        FROM event_attendees ea
        JOIN users u ON ea.userId = u.id
        WHERE ea.eventId = ?
      `).all(req.params.id);

      res.json(attendees);
    } catch (err: any) { res.status(500).json({ error: err.message }); }
  });

  app.get("/api/users/:id/events", (req: any, res) => {
    try {
      const events = db.prepare("SELECT events.*, users.name as hostName FROM events LEFT JOIN users ON events.hostId = users.id WHERE events.hostId = ?").all(req.params.id);
      const parsedEvents = events.map((e: any) => ({
        ...e,
        isFeatured: !!e.isFeatured,
        tags: e.tags ? JSON.parse(e.tags) : [],
        sponsorshipSettings: e.sponsorshipSettings ? JSON.parse(e.sponsorshipSettings) : undefined
      }));
      res.json(parsedEvents);
    } catch (err: any) { res.status(500).json({ error: err.message }); }
  });

  app.get("/api/users/:id", (req: any, res) => {
    const user = db.prepare("SELECT * FROM users WHERE id = ?").get(req.params.id) as any;
    if (user) {
      const attended = db.prepare("SELECT eventId FROM event_attendees WHERE userId = ?").all(user.id).map((r: any) => r.eventId);
      res.json({
        ...user,
        savedEventIds: user.savedEventIds ? JSON.parse(user.savedEventIds) : [],
        attendedEventIds: attended.length > 0 ? attended : (user.attendedEventIds ? JSON.parse(user.attendedEventIds) : []),
        hostedEventIds: user.hostedEventIds ? JSON.parse(user.hostedEventIds) : [],
        interests: user.interests ? JSON.parse(user.interests) : []
      });
    } else {
      res.status(404).json({ error: "User not found" });
    }
  });

  app.put("/api/events/:id", authenticate, (req: any, res) => {
    const event = req.body;
    const id = req.params.id;
    const existing = db.prepare("SELECT * FROM events WHERE id = ?").get(id) as any;

    if (!existing) return res.status(404).json({ error: "Event not found" });
    if (existing.hostId !== req.userId) return res.status(403).json({ error: "Unauthorized: You do not own this event" });

    const stmt = db.prepare(`
      UPDATE events SET 
        title = ?, description = ?, date = ?, time = ?, location = ?, venueName = ?, 
        format = ?, imageUrl = ?, price = ?, category = ?, sponsorId = ?, 
        capacity = ?, tags = ?, isFeatured = ?, sponsorshipSettings = ?, visibility = ?, updatedAt = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    try {
      stmt.run(
        event.title, event.description, event.date, event.time, event.location,
        event.venueName || null, event.format, event.imageUrl || null, event.price || 0,
        event.category, event.sponsorId || null, event.capacity || null,
        event.tags ? JSON.stringify(event.tags) : JSON.stringify([]),
        event.isFeatured ? 1 : 0,
        event.sponsorshipSettings ? JSON.stringify(event.sponsorshipSettings) : null,
        event.visibility || existing.visibility,
        id
      );
      res.json({ success: true });
    } catch (error: any) { res.status(500).json({ error: error.message }); }
  });

  app.delete("/api/events/:id", authenticate, (req: any, res) => {
    const id = req.params.id;
    const existing = db.prepare("SELECT * FROM events WHERE id = ?").get(id) as any;

    if (!existing) return res.status(404).json({ error: "Event not found" });
    if (existing.hostId !== req.userId) return res.status(403).json({ error: "Unauthorized: You do not own this event" });

    try {
      db.prepare("DELETE FROM events WHERE id = ?").run(id);
      db.prepare("DELETE FROM event_attendees WHERE eventId = ?").run(id);
      res.json({ success: true });
    } catch (error: any) { res.status(500).json({ error: error.message }); }
  });

  app.post("/api/users", (req, res) => {
    const user = req.body;
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO users (
        id, name, email, avatarUrl, savedEventIds, attendedEventIds, hostedEventIds
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    try {
      stmt.run(
        user.id,
        user.name,
        user.email,
        user.avatarUrl || null,
        JSON.stringify(user.savedEventIds || []),
        JSON.stringify(user.attendedEventIds || []),
        JSON.stringify(user.hostedEventIds || [])
      );
      res.status(201).json({ success: true });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/users/attend", authenticate, (req: any, res) => {
    const { eventId } = req.body;
    const userId = req.userId;
    const user = db.prepare("SELECT * FROM users WHERE id = ?").get(userId) as any;
    if (!user) return res.status(404).json({ error: "User not found" });

    // Check if already attending via new table
    const existing = db.prepare("SELECT * FROM event_attendees WHERE eventId = ? AND userId = ?").get(eventId, userId);

    if (!existing) {
      try {
        db.prepare("INSERT INTO event_attendees (eventId, userId) VALUES (?, ?)").run(eventId, userId);
        db.prepare("UPDATE events SET attendees = attendees + 1 WHERE id = ?").run(eventId);
      } catch (e) {
        console.error("Failed to register attendee:", e);
      }
    }

    const attendedEventRows = db.prepare("SELECT eventId FROM event_attendees WHERE userId = ?").all(userId) as any[];
    const attendedEventIds = attendedEventRows.map(r => r.eventId);
    res.json({ success: true, attendedEventIds });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, "dist")));
    app.get("*", (req, res) => {
      res.sendFile(path.join(__dirname, "dist", "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
