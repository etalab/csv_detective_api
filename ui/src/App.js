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
      openAbout: false,
      openPerf: false,

      result: "",
      
    };
    this.handleChange = this.handleChange.bind(this);  
    this.handlePredictClick = this.handlePredictClick.bind(this);
  }

  onDrop = (acceptedFiles) => {
    let formData = new FormData();
    formData.append('resource_csv', acceptedFiles[0])
    this.state.formData.resource_id = acceptedFiles[0].name
    // formData.resource_csv = acceptedFiles[0];
    this.setState({ isLoading: true });
    fetch(`http://127.0.0.1:5000/csv_detective/`, 
      {
        method: 'POST',
        body: formData
      })
      .then(response =>  response.json())
      .then(result => this.setState({ result, isLoading: false }))
      .catch(console.log)
    // console.log(acceptedFiles);
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

  updateOpenAbout = () =>
  {
    this.setState({openAbout: !this.state.openAbout})
  }


  updateOpenPerf = () =>
  {
    this.setState({openPerf: !this.state.openPerf})
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
    // this.setState({ open: !this.state.open});
    formData.resource_id = formData.resource_id !== "" ? formData.resource_id : "1f0ebe13-e1f3-4adb-833a-dfc1ce8020fa";
    fetch(`http://127.0.0.1:5000/csv_detective/?resource_id=${formData.resource_id}`, 
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
  
  render() {
    
    const isLoading = this.state.isLoading;
    const formData = this.state.formData;
    const result = this.state.result;
    const openAbout = this.state.openAbout;
    const openPerf = this.state.openPerf;
    
    return (

    <Container>
        <div className="title">
          <h5>CSV Detective API<sup><font size="1">BETA</font></sup> (Updated 2019-08-21)</h5>
        </div>
        <div className="input_content">
        <Form>
          <Form.Row>
            <Form.Group as={Col}>
              <Form.Label>Enter a <a href="https://www.data.gouv.fr" target="_blank">data.gouv.fr</a> CSV resource ID:</Form.Label>
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
                  {!isDragActive && (<div>Or upload a CSV by clicking or dropping it <font color="#0000EE">here</font> (max 5mb)</div>)}
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
          if (result !== "" && Object.keys(result["columns_ml"]).length !== 0)
          {
            return(
            <div className="results_content">
              <Row>
                  <Col><h3>Identified Columns (ML Based)</h3></Col>
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
                      </tr>
                    </thead>
                    <tbody>
                    {this.handleCSVResponse(result, "columns_ml")}
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

       
        
        
        <div className="description_content">
        <Row>
            <Col><h3 onClick={this.updateOpenAbout}>About</h3></Col>
        </Row>
        <Collapse in={openAbout}>
          <div>
          <Row>
            <Col><h5>What?</h5>

            <a href="https://github.com/etalab/csv_detective">CSV Detective</a> is a tool that gives you information about a CSV, such as its encoding and separator, as well as the type of columns contained inside: whether there are columns containing a <i>SIRET</i> or a <i>SIREN</i> number, a postal code, a department or a commune name, a geographic position, etc. 
            This UI builds on CSV Detective. We improved it, APIfied it, and throught this interface, allow a friendlier use. Also a machine learning model to detect types was added (which is work in progress).

          </Col>
          </Row>
            <Row>
            <Col><h5>Why?</h5>
            This tool was developed  with <a href="https://www.data.gouv.fr" target="_blank">data.gouv.fr</a> (DGF) in mind. Being a repository of open datasets is one of the main tasks of DGF. In that sense, knowing what is inside the large collection of CSVs it contains can be useful for several tasks:
            <ul>
              <li><b>Enrich</b> the results of the <b>search engine</b> with the contents of the CSVs.</li>
              <li><b>Link datasets together</b> according to their values.</li>
              <li><b>Link datasets</b> with well-maintained, trustable <b>reference datasets</b>.</li>
              <li><b>Group datasets together</b> according to their general topic.</li>
            </ul>
            </Col>
            </Row> 
            <Row>
            <Col><h5>How?</h5>
            CSV Detective has two strategies to detect a column type:
            <ol>
              <li><b>Rules + References</b>: using regular expressions and also comparing the values with reference data (e.g., if the value <i>69007</i> appears in a list of postal codes, then it is a postal code.</li>
              <li><b>Supervised Learning (In progress)</b>: manually tagging columnt types and then determining simple features coupled to the content of the cells themselves to train classification algorithms.</li>
            </ol>
            </Col>
            </Row>
            <Row><Col><h5>Where?</h5>
            The code lives <a href="https://github.com/psorianom/csv_detective_api" target="_blank">here</a>.
            
            </Col></Row>
            </div>
          </Collapse>
        </div>
        
        <div className="performance_content">
          <Row>
            <Col><h3 onClick={this.updateOpenPerf}>Current Performance</h3></Col>
          </Row>
          <Collapse in={openPerf}>
          <div>
            <Row>
              <Col>
                <p>Rule Based</p>
                <img src="https://img.shields.io/badge/F--score-84.1-green"></img>
              </Col>
              <Col>
                <p>Machine Learning Based</p>
                <img src="https://img.shields.io/badge/F--score-87.7-green"></img>
              </Col>
            </Row>
          </div>
          </Collapse>
          
        </div>
    </Container>
    );
  }
}

export default App;
