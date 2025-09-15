// admin.tsx
import ReactDOM from 'react-dom/client';
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Editor from './Editor'; // тут будет твой Admin компонент или другие редакторы

const AdminRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin" element={<Editor />} />
      </Routes>
    </BrowserRouter>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<AdminRouter />);
