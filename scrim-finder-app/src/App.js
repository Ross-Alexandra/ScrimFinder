import React, {Component} from 'react';
import ScrimInformation from './PageBodies/ScrimInformation/ScrimInformation';
import NavBar from './NavBar';

import './App.css';

class App extends Component {
    render() {
        return (
            <div className="App-body">
                <div className="App-header">
                    <NavBar/>
                </div>
                <div className="App-body">
                    <ScrimInformation/>
                </div>
            </div>
        );
    }
}

export default App;
