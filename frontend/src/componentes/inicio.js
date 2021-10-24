import React from 'react';
import '../css/comun.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import Form from 'react-bootstrap/Form';


export default function Inicio(){
    return(
        <>
        <Form>

            <Form.Group controlId="formGridEmail">
                <Form.Label style={{ color: 'black' }}>Nombre: Rodolfo Alexander Avalos Soto</Form.Label>  <br />
                <Form.Label style={{ color: 'black' }}>Carnet: 20180210</Form.Label> <br />
                <Form.Label style={{ color: 'black' }}>Universidad: San Carlos De Guatemala</Form.Label> <br />
                <Form.Label style={{ color: 'black' }}>Carrea: Ingenieria en Ciencas y Sistemas</Form.Label> <br />
                <Form.Label style={{ color: 'black' }}>Segundo Semestre 2021</Form.Label> <br />
                <Form.Label style={{ color: 'black' }} >Seccion C</Form.Label>
                 <br />
            </Form.Group>

    </Form>
    </>
    )
}
