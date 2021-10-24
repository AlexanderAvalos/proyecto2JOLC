import React from 'react';
import {BrowserRouter,Switch,Route} from 'react-router-dom';
import Inicio from '../App'
import Analisis from '../componentes/analisis'

function Routes(){
    return(
        <BrowserRouter>
            <Switch>
                <Route exact path ="/" component={Inicio}></Route>
                <Route exact path ="/Analisis" component={Analisis}></Route>
            </Switch>
        </BrowserRouter>
    );
}


export default Routes;