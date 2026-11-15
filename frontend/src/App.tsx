import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { PosBilling } from './pages/PosBilling';
import { Customers } from './pages/Customers';
import { Items } from './pages/Items';
import { Stock } from './pages/Stock';
import { CashBook } from './pages/CashBook';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="pos" element={<PosBilling />} />
            <Route path="customers" element={<Customers />} />
            <Route path="items" element={<Items />} />
            <Route path="stock" element={<Stock />} />
            <Route path="cashbook" element={<CashBook />} />
            <Route path="reports" element={<Reports />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
