import React, { Component } from 'react';
import './App.css';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Collapse from 'react-bootstrap/Collapse';
import Table from 'react-bootstrap/Table';
import ReactJson from 'react-json-view';
import 'bootstrap/dist/css/bootstrap.css';

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

  // getRreferenceDatesets = (referenceDatasets)

  handleCSVResponse = (response, detected_type) =>
  {
    if (!(detected_type in response))
      return null
    
    return Object.entries(response[detected_type]).map((key_value, index) =>
    {
      return(
      <tr key={index}>
        <td>{key_value[0]}</td>
        <td>{key_value[1]}</td>
      </tr>
      )
    })
  }

  getReferenceDatasets = (response) =>
  {
    let reference_datasets = response.reference_matched_datasets["reference_datasets"];
    let matched_datasets = response.reference_matched_datasets["matched_datasets"]

    return Object.entries(matched_datasets).map((key_value) =>
    {
      let ref_ds_id = key_value[0];  // this is an int
      let col_types = key_value[1];  // this is a list
      let col_types_str = col_types.join(", ");
      let column_type_str = (col_types.length === 1) ? "type" : "types";
      let ref_dataset = reference_datasets[ref_ds_id]
      return(
        <p>The column {column_type_str} <b>{col_types_str}</b> could be referenced by the dataset <b><a href={ref_dataset["url"]}>{ref_dataset["name"]}</a></b>.</p>
      )
    }
    )
  }

  handlePredictClick = (event) => {
    const formData = this.state.formData;
    this.setState({ isLoading: true });
    this.setState({ open: !this.state.open});
    fetch(`http://127.0.0.1:5000/csv_linker/?resource_id=${formData.textfield1}`, 
      {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        method: 'GET'
      })
      .then(response =>  response.json())
      .then(result => this.setState({ result, isLoading: false }))
      .catch(console.log)
    console.log(this.state.result)
    
    
  }
  
  modifi() {
    // const greeting = 'Hello Function Component!';
    // this.setState({ result: "foook" });

    return (
      <h5> OMG</h5>
    );
  }

  render() {
    
    const isLoading = this.state.isLoading;
    const formData = this.state.formData;
    const result = this.state.result;
    const open = this.state.open;
    
    return (

    <Container>
        <div className="title">
          <h5>CSV Detective API<sup><font size="1">BETA</font></sup> (Updated 2019-08-21)</h5>
        </div>
        <div className="input_content">
        <Form>
          <Form.Row>
            <Form.Group as={Col}>
              <Form.Label>Enter a <a href="https://www.data.gouv.fr">data.gouv.fr</a> CSV resource ID:</Form.Label>
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
                  onClick={!isLoading ? this.handlePredictClick : null}>
                  { isLoading ? 'Making analysis' : 'Submit' }
              </Button>
            </Form.Group>
          </Form.Row>
        </Form>
        </div>

        <Collapse in={open}>
        <div className="results_content">
            <Row>
                <Col><h3>Metadata</h3></Col>
            </Row>
            <Row>
              {
                (() => {
                  if (result !== "" && Object.keys(result["metadata"]).length !== 0)
                  {
                    return(
                      <Col>
                      <ReactJson src={result["metadata"]} collapsed={1} name={false} displayDataTypes={false} />
                      </Col>

                    )
                  }
                })()
              }
            </Row>
        </div>
        </Collapse>

        <Collapse in={open}>
          <div className="results_content">
            <Row>
                <Col><h3>Identified Columns</h3></Col>
            </Row>
            <Row>
              <Col>
              {
                result === "" ? null :
                (
                  <Table hover size="sm">
                  <thead>
                    <tr>
                      <th>Column Name</th>
                      <th>Type Detected</th>
                      {/* <th>Reference Dataset</th> */}
                    </tr>
                  </thead>
                  <tbody>
                  {this.handleCSVResponse(result, "columns_rb")}
                  </tbody>
                </Table>
                )
              }
              </Col>
            </Row>
          </div>
        </Collapse>
        
        <Collapse in={open}>
        <div className="results_content">
            <Row>
                <Col><h3>Reference Datasets</h3></Col>
            </Row>
            <Row>
              {
                (() => {
                  if (result !== "" && Object.keys(result["reference_matched_datasets"]["matched_datasets"]).length !== 0)
                  {
                    return(
                      <Col>
                      {this.getReferenceDatasets(result)}
                      </Col>

                    )
                  }
                })()
              }
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
          <Row>
            {this.modifi()}
          </Row>
        </div>
        {
          //   (<Row>
          //     <Col className="result-container">
          //       <h5 id="result">{result}</h5>
          //     </Col>
            // </Row>)
        }

    </Container>
    );
  }
}

export default App;
