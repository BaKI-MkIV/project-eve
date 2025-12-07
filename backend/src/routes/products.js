import express from 'express';
import pool from '../db.js';

const router = express.Router();

// Получить все товары
router.get('/', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM products ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Создать товар
router.post('/', async (req, res) => {
  const { id, name, description, base_price } = req.body;
  try {
    const query = `
      INSERT INTO products (id, name, description, base_price)
      VALUES ($1, $2, $3, $4)
      RETURNING *`;
    const result = await pool.query(query, [id, name, description, base_price]);
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Удалить товар
router.delete('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await pool.query('DELETE FROM products WHERE id = $1', [id]);
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

