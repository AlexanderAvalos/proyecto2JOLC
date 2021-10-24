import React, { Component, useState , useEffect} from 'react';
import './css/comun.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import Navbar from 'react-bootstrap/Navbar'
import Nav from 'react-bootstrap/Nav'
import NavDropdown from 'react-bootstrap/NavDropdown'
import Container from 'react-bootstrap/esm/Container';
import Form from 'react-bootstrap/Form';
import analisis from './componentes/analisis'
import Inicio from './componentes/inicio'
import {Link, Route} from "wouter"

function App() {
  const redireccionInicio = () => {
    window.location.href = `http://localhost:3000/`
  }
  const redireccionAnalisis = () => {
    window.location.href = `http://localhost:3000/analisis`
  }
  return (
    <>
                <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark" >
                    <Navbar.Brand > PROYECTO 2 </Navbar.Brand>
                    <Navbar.Toggle aria-controls="responsive-navbar-nav" />
                    <Navbar.Collapse id="responsive-navbar-nav"  >
                        <Nav className="mr-auto">
                          <Nav.Link onClick={redireccionInicio} >inicio</Nav.Link>
                          <Nav.Link onClick={redireccionAnalisis}  >Analisis</Nav.Link>
                          <NavDropdown title="Reportes" id="collasible-nav-dropdown">
                                <NavDropdown.Item>Errores</NavDropdown.Item>
                                <NavDropdown.Item >Tabla de Simbolos</NavDropdown.Item>
                                <NavDropdown.Item >AST</NavDropdown.Item>
                            </NavDropdown>
                        </Nav>
                    </Navbar.Collapse>
                </Navbar>
                <br />

                  <Container>
                  <Route exact path ="/analisis" component={analisis}></Route>
                  <Route exact path ="/" component = {Inicio}></Route>  
                  </Container> 
            </>
  );
}

export default App;
