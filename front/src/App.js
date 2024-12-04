import React from 'react'
import Pointage from './components/Pointage/Pointage'
import "./App.css"
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Individu from './components/Individu/Individu'
import 'toastr/build/toastr.min.css';
import ProtectedRoute from './routing/ProtectedRoute'
const App = () => {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="*" element={<Pointage/>} />
        <Route path="/individu" element={<ProtectedRoute children={<Individu/>}/>} />
      </Routes>

    </BrowserRouter>
  )
}

export default App
