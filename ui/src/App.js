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
import Dropzone from 'react-dropzone'

class App extends Component {

  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      formData: {resource_id: ''},
      open: false,
      result: "",
      
    };
    this.handleChange = this.handleChange.bind(this);  
    this.handlePredictClick = this.handlePredictClick.bind(this);
  }

  onDrop = (acceptedFiles) => {
    console.log(acceptedFiles);
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
    formData.resource_id = formData.resource_id !== "" ? formData.resource_id : "1f0ebe13-e1f3-4adb-833a-dfc1ce8020fa";
    fetch(`http://127.0.0.1:5000/csv_linker/?resource_id=${formData.resource_id}`, 
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
                name="resource_id"
                value={formData.resource_id}
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
          <Form.Row>
            <Form.Group as={Col}>
              <Dropzone onDrop={this.onDrop} accept="text/csv" maxSize={5242880}>
              {({getRootProps, getInputProps, isDragActive, isDragReject, rejectedFiles}) => {
                const isFileTooLarge = rejectedFiles.length > 0 && rejectedFiles[0].size > 5242880;
                return(
                <div {...getRootProps()}>
                  <input {...getInputProps()} />
                  {!isDragActive && (<div>Or click <font color="#0000EE">here</font> or drop a CSV to upload (max 5mb)</div>)}
                  {isDragActive && !isDragReject && "Drop it like it's hot!"}
                  {isDragReject && "File type not accepted, sorry!"}
                  {isFileTooLarge && (
                    <div className="text-danger mt-2">
                      File is too large.
                    </div>
                  )}
                </div> 
                ) 
                }
                }
              </Dropzone>
            </Form.Group>
          </Form.Row>
          <Form.Row>
          </Form.Row>
        </Form>
        </div>
        {
          (() => {
            if (result !== "" && Object.keys(result["metadata"]).length !== 0)
            {
              return(
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
              )
            }
        })()
      }

      {
        (() => {
          if (result !== "")
          {
            return(
            <div className="results_content">
              <Row>
                  <Col><h3>Identified Columns (Rule Based)</h3></Col>
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
            )
           }
        })()
      } 
        
      {
        (() => {
          if (result !== "")
        { 
          return(
            <div className="results_content">
                <Row>
                    <Col><h3>Reference Datasets</h3></Col>
                </Row>
                <Row>
                  {
                    (() => {
                        if(Object.keys(result["reference_matched_datasets"]["matched_datasets"]).length !== 0)
                        {
                          return(
                            <Col>
                            {this.getReferenceDatasets(result)}
                            </Col>

                          )
                        }
                        else
                        {
                          return(<Col>No reference datasets where found for your dataset ¯\_(ツ)_/¯</Col>)
                        }
                    })()
                  }
                </Row>
            </div>
          )
        }
      })()
      } 

{
        (() => {
          if (result !== "")
        { 
          return(
            <div className="results_content_ml">
                <Row>
                    <Col><h3>Identified Columns (ML)</h3></Col>
                </Row>
                <Row>
                  {
                    (() => {
                        if(Object.keys(result["reference_matched_datasets"]["matched_datasets"]).length !== 0)
                        {
                          return(
                            <Col>
                            {this.getReferenceDatasets(result)}
                            </Col>

                          )
                        }
                        else
                        {
                          return(<Col>No reference datasets where found for your dataset ¯\_(ツ)_/¯</Col>)
                        }
                    })()
                  }
                </Row>
            </div>
          )
        }
      })()
      } 
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
