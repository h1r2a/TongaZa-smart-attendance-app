import React from 'react'
import "./navbar.css"
import { useNavigate } from 'react-router-dom'
const Navbar = () => {

    const navigate = useNavigate();

  return (
    <div className='navbar'>
      <div className="logo"  onClick={()=>{navigate("/")}}>
        <h1>TongaZa</h1>
      </div>

      <div className="individu">
        <button onClick={()=>{navigate("/individu")}}>Individu</button>
      </div>
    </div>
  )
}

export default Navbar
