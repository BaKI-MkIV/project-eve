import express from 'express';
import cors from 'cors';
import productsRouter from './routes/products.js';

const app = express();

app.use(cors());
app.use(express.json());

// Простая проверка API
app.get('/', (req, res) => {
  res.json({ now: new Date().toISOString() });
});

// Подключаем CRUD
app.use('/products', productsRouter);

const port = 4000;
app.listen(port, () => {
  console.log(`Backend running on port ${port}`);
});

