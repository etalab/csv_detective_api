import React, { useState } from "react";
import Collapse from "react-bootstrap/Collapse";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";

const About = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="description_content">
      <Row>
        <Col>
          <h3 onClick={() => setOpen(!open)}>About</h3>
        </Col>
      </Row>
      <Collapse in={open}>
        <div>
          <Row>
            <Col>
              <h5>What?</h5>
              <a href="https://github.com/etalab/csv_detective">
                CSV Detective
              </a>{" "}
              is a tool that gives you information about a CSV, such as its
              encoding and separator, as well as the type of columns contained
              inside: whether there are columns containing a <i>SIRET</i> or a{" "}
              <i>SIREN</i> number, a postal code, a department or a commune
              name, a geographic position, etc.
              <p>
                This UI builds on CSV Detective. We improved it, APIfied it, and
                through this interface, you can get a glimpse of how it works.
                Also, we added a machine learning model as an alternative (this
                is work in progress).
              </p>
            </Col>
          </Row>
          <Row>
            <Col>
              <h5>Why?</h5>
              This tool was developed with{" "}
              <a
                href="https://www.data.gouv.fr"
                target="_blank"
                rel="noopener noreferrer"
              >
                data.gouv.fr
              </a>{" "}
              (DGF) in mind. One of the main tasks of DGF is being a repository
              of open datasets. These datasets are often contained within CSV
              files. Knowing what is inside this large collection of CSVs can be
              useful for several tasks:
              <ul>
                <li>
                  <b>Enrich</b> the results of DGF <b>search engine</b> with the
                  contents of the CSVs.
                </li>
                <li>
                  <b>Link datasets together</b> according to their values.
                </li>
                <li>
                  <b>Link datasets</b> with well-maintained, trustable{" "}
                  <b>reference datasets</b>.
                </li>
                <li>
                  <b>Group datasets together</b> according to their general
                  topic.
                </li>
              </ul>
            </Col>
          </Row>
          <Row>
            <Col>
              <h5>How?</h5>
              The UI has two modes of functioning: you can enter a DGF resource
              ID and click the button below or you can load a CSV file by
              clicking in the corresponding area. The process in both cases will
              start automatically. Behind the scenes, CSV Detective has two
              strategies to detect a column type:
              <ol>
                <li>
                  <b>Rules + References</b>: using regular expressions and also
                  comparing the values with reference data (e.g., if the value{" "}
                  <i>69007</i> appears in a list of postal codes, then it is a
                  postal code.
                </li>
                <li>
                  <b>Marchine Learning (In progress)</b>: manually tagging
                  columnt types and then determining simple features coupled to
                  the content of the cells themselves to train classification
                  algorithms.
                </li>
              </ol>
            </Col>
          </Row>
          <Row>
            <Col>
              <h5>Who?</h5>
              Etalab's Data Science, Datagouv, and Open Data teams are working
              on this. The code lives{" "}
              <a
                href="https://github.com/psorianom/csv_detective_api"
                target="_blank"
                rel="noopener noreferrer"
              >
                here
              </a>{" "}
              for now.
            </Col>
          </Row>
        </div>
      </Collapse>
    </div>
  );
};

export default About;
