
import logo from './logo.svg';

import React, { Component } from 'react';
import './App.css';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse'
import 'bootstrap/dist/css/bootstrap.css';

// function modifi() {
//   const greeting = 'Hello Function Component!';
//   // this.state.result = "foook";
//   return <h1>{greeting}</h1>;
// }

class App extends Component {

  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      formData: {
        textfield1: '1f0ebe13-e1f3-4adb-833a-dfc1ce8020fa',
        textfield2: '',
        select1: 1,
        select2: 1,
        select3: 1},
      open: false,
      result: ""
    };
    this.handleChange = this.handleChange.bind(this);  
    this.handlePredictClick = this.handlePredictClick.bind(this);
  }

  

  handleChange = (event) => {
    const value = event.target.value;
    const name = event.target.name;
    var formData = this.state.formData;
    formData[name] = value;
    this.setState({
      formData
    });
  }

  handlePredictClick = (event) => {
    const formData = this.state.formData;
    // this.setState({ isLoading: true });
    var result = "";
    this.setState({ open: !this.state.open});
    fetch(`http://127.0.0.1:5000/csv_linker/?resource_id=${formData.textfield1}`, 
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        method: 'GET'
      })
      .then(response => response.json())
      .then(response => {
        result = Object.keys(response).map((key, index) =>
          {return(<p key={index}> This is my key {key} and this is value {response[key]}</p>)}
        )
      // this.setState({result: foo});
      })
      .catch(console.log)
    
    // this.setState({result: result, isLoading: false})
    console.log("this", this)
  }
  
  modifi() {
    const greeting = 'Hello Function Component!';
    this.setState({ result: "foook" });

    return <h1>{greeting}</h1>;
  }

  render() {
    const isLoading = this.state.isLoading;
    const formData = this.state.formData;
    const result = this.state.result;
    const open = this.state.open;
    return (
      <Container>
        <div className="title">
          <h1>DGF Column Linker</h1>
        </div>
        <div className="input_content">
        <Form>
          <Form.Row>
            <Form.Group as={Col}>
              <Form.Label>Enter a <a href="https://www.data.gouv.fr">data.gouv.fr</a> resource ID:</Form.Label>
              <Form.Control
                type="text"
                placeholder="e.g., 1f0ebe13-e1f3-4adb-833a-dfc1ce8020fa"
                name="textfield1"
                value={formData.textfield1}
                onChange={this.handleChange}
                />
            </Form.Group>
          </Form.Row>
          <Form.Row>
            <Form.Group as ={Col}>
              <Button
                  block
                  variant="success"
                  disabled={isLoading}
                  onClick={!isLoading ? this.handlePredictClick.bind(this) : null}>
                  { isLoading ? 'Making analysis' : 'Analyze' }
              </Button>
            </Form.Group>
          </Form.Row>
        </Form>
        </div>
        <Collapse in={open}>
          <div className="results_content">
            <Row>
                <Col><h3>Results</h3></Col>
            </Row>
            <Row>
              <Form.Group as={Col}>

              </Form.Group>
            </Row>
          </div>
        </Collapse>
        <div className="description_content">
          <Row>
              <Col><h3>About</h3></Col>
          </Row>
          <Row>
            <Col><h6>What?</h6></Col>
            <Col><h6>Why?</h6></Col>
            <Col><h6>How?</h6></Col>
            <Col><h6>Where?</h6></Col>
          </Row>
        </div>
        <div className="performance_content">
          <Row>
          <Col>
            <h3>Performance</h3>
          </Col>
          </Row>
        </div>
        {
          result === "" ? null :
            (<Row>
              <Col className="result-container">
                <h5 id="result">{result}</h5>
              </Col>
            </Row>)
        }

    </Container>
    );
  }
}
// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

export default App;
