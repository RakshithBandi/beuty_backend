const express = require('express');
const cors = require('cors');
const { open } = require('sqlite');
const sqlite3 = require('sqlite3');
const path = require('path');

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());

let db;

(async () => {
  db = await open({
    filename: path.join(__dirname, 'database.sqlite'),
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      price TEXT,
      duration TEXT,
      staff TEXT,
      img TEXT
    );

    CREATE TABLE IF NOT EXISTS bookings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      serviceId INTEGER,
      client TEXT,
      date TEXT,
      price TEXT,
      FOREIGN KEY(serviceId) REFERENCES services(id)
    );

    CREATE TABLE IF NOT EXISTS customers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      email TEXT UNIQUE,
      phone TEXT,
      lastVisit TEXT
    );
  `);

  // Seed data if empty
  const servicesCount = await db.get('SELECT COUNT(*) as count FROM services');
  if (servicesCount.count === 0) {
    await db.run('INSERT INTO services (name, price, duration, staff, img) VALUES (?, ?, ?, ?, ?)', ['Hair Styling & Cutting', '$85.00', '60 min', 'Samantha W.', '/images/salon_service.png']);
    await db.run('INSERT INTO services (name, price, duration, staff, img) VALUES (?, ?, ?, ?, ?)', ['Luxury Spa Facial', '$120.00', '90 min', 'Jessica K.', '/images/spa_service.png']);
    await db.run('INSERT INTO services (name, price, duration, staff, img) VALUES (?, ?, ?, ?, ?)', ['Premium Manicure', '$45.00', '45 min', 'Lisa T.', '/images/nail_service.png']);
  }

  console.log('Database initialized');
})();

// Services API
app.get('/api/services', async (req, res) => {
  const services = await db.all('SELECT * FROM services');
  res.json(services);
});

app.post('/api/services', async (req, res) => {
  const { name, price, duration, staff, img } = req.body;
  const result = await db.run('INSERT INTO services (name, price, duration, staff, img) VALUES (?, ?, ?, ?, ?)', [name, price, duration, staff, img]);
  res.json({ id: result.lastID, ...req.body });
});

app.put('/api/services/:id', async (req, res) => {
  const { name, price, duration, staff, img } = req.body;
  await db.run('UPDATE services SET name=?, price=?, duration=?, staff=?, img=? WHERE id=?', [name, price, duration, staff, img, req.params.id]);
  res.json({ success: true });
});

// Bookings API
app.get('/api/bookings', async (req, res) => {
  const bookings = await db.all('SELECT bookings.*, services.name as serviceName FROM bookings JOIN services ON bookings.serviceId = services.id');
  res.json(bookings);
});

app.post('/api/bookings', async (req, res) => {
  const { serviceId, client, date, price } = req.body;
  const result = await db.run('INSERT INTO bookings (serviceId, client, date, price) VALUES (?, ?, ?, ?)', [serviceId, client, date, price]);
  
  // Also track customer
  const customer = await db.get('SELECT * FROM customers WHERE name = ?', [client]);
  if (!customer) {
    await db.run('INSERT INTO customers (name, lastVisit) VALUES (?, ?)', [client, date]);
  } else {
    await db.run('UPDATE customers SET lastVisit = ? WHERE name = ?', [date, client]);
  }
  
  res.json({ id: result.lastID, ...req.body });
});

// Customers API
app.get('/api/customers', async (req, res) => {
  const customers = await db.all('SELECT * FROM customers');
  res.json(customers);
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
