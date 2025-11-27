/**
 * API Routes
 * NEW API ENDPOINTS: Should trigger ⚠️ API changes observation
 */

const express = require('express');
const router = express.Router();

// EXISTING endpoint (for context)
router.get('/api/users', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});

// NEW: Public API endpoint added
router.post('/api/users', async (req, res) => {
  const { email, name } = req.body;
  const user = await User.create({ email, name });
  res.status(201).json(user);
});

// NEW: Public API endpoint added
router.delete('/api/users/:id', async (req, res) => {
  await User.destroy({ where: { id: req.params.id } });
  res.status(204).send();
});

// NEW: Public API endpoint added
router.patch('/api/users/:id', async (req, res) => {
  const user = await User.update(req.body, {
    where: { id: req.params.id }
  });
  res.json(user);
});

module.exports = router;
