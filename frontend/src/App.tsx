import { useState } from "react";
import reactLogo from "./assets/react.svg";
import "./App.css";
import Message from "./components/hidden/Message";
import ListGroup from "./components/hidden/ListGroup";
import Alert from "./components/hidden/Alert";
import Button from "./components/hidden/Button";

import Header from "./components/Header";
import DocumentTools from "./components/DocumentTools";
import IndexQuery from "./components/IndexQuery";
import "./style.scss";

function App() {
  let items = ["Mari a", "Mari b", "Mari c", "Mari d"];

  // Hooks
  const [count, setCount] = useState(0);
  const [showAlert, setShowAlert] = useState(false);

  // Handlers
  const handleSelectItem = (item: string) => {
    console.log(item);
  };

  const handleClick = () => {
    console.log("Clicked");
    setShowAlert(true);
  };

  const handleClose = () => {
    console.log("Close");
    setShowAlert(false);
  };

  return (
    <div className="app">
      <div className="teste">
        <ListGroup
          items={items}
          heading="Lista"
          onSelectItem={handleSelectItem}
        />
        {showAlert && (
          <Alert onClose={handleClose}>
            Danger <span>Alou</span>
          </Alert>
        )}
        <Button color="dark" children="Danger Button" onClick={handleClick} />
      </div>

      <Header />
      <div className="content">
        <DocumentTools />
        <IndexQuery />
      </div>
    </div>
  );
}

export default App;
