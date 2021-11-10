import React, { Component, useEffect  ,useState } from 'react';
import '../css/comun.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import Container from 'react-bootstrap/esm/Container';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col'
import axios from 'axios';
import { Graphviz } from 'graphviz-react';
import {saveAs} from 'file-saver';


const URL = "http://localhost:5000/serv"

export default function Analisis(){
    const [valor,setvalue] = useState('');
    const [valor2,SetValor] = useState('');
    const [te,setTE] = useState('digraph{}');
    const [ts,setTS] = useState('digraph{}');

    async function traducir(){
        const obj = {valor}
        const {data} = await axios.post(URL,obj)
        SetValor(data)
    }

    async function tablaSimbolo(){
        const {data} = await axios.get(URL + '/simbolo')
        setTS( data )
    }
    async function tablaErrores(){
        const {data} = await axios.get(URL + '/error')
        setTE(data)
    }


    const guardarfile = () =>{
        const blob = new Blob([ts]);
        saveAs(blob, 'TablaSimbolo.dot');
        const blob2 = new Blob([te]);
        saveAs(blob2, 'TablaErrores.dot');
    }

    const readFile = (e) =>{
        const file = e.target.files[0];
        if(!file) return;
        const fileReader = new FileReader();
        fileReader.readAsText(file)

        fileReader.onload = () =>{
            console.log(fileReader.result)
            setvalue(fileReader.result)
        }

        fileReader.onerror =()=>{
            console.log(fileReader.error)
        }

    }

        return (
            <>
                <Container> <Row>
                        <Col>
                        <div className="form-group">
                        <Form.Label style={{ color: 'white' }} column="lg" lg={2}>Entrada</Form.Label>  <br />
                            <Form.Control as="textarea" rows={3} name="analizador"  value = {valor} onChange = {(e)=> setvalue(e.target.value)}/><br />
                            <input type = "file" multiple= {false} onChange={readFile} />
                        </div>
                        </Col>
                        <Col>
                        <div className="form-group">
                        <Form.Label style={{ color: 'white' }} column="lg" lg={2}>Consola</Form.Label>  <br />
                            <div className="graph">
                            <Form.Control as="textarea" rows={3} name="consola" value = {valor2} onChange = {(e)=> SetValor(e.target.valor2)} /><br />
                            <Button variant="primary" onClick={traducir}> Traducir</Button> &nbsp;
                            <Button variant="secondary" onClick={tablaSimbolo}> Tabla Simbolos</Button> &nbsp;
                            <Button variant="danger" onClick={tablaErrores}> Tabla Errores</Button> &nbsp;
                            <Button variant="success" onClick={guardarfile}> Generar dot</Button><br/>
                            </div>
                        </div >
                        </Col>
                    </Row>
                    
                    
                </Container>
                                <div>
                <Graphviz dot={ts}/>
                <Graphviz dot={te}/></div>
                
                
                
            </>
        );
    
}
